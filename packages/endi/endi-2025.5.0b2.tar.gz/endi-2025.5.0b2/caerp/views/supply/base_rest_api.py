import colander
import datetime
import logging

from pyramid.csrf import get_csrf_token
from pyramid.httpexceptions import HTTPForbidden

from caerp.controllers.expense_types import ExpenseTypeQueryService
from caerp.controllers.state_managers import (
    get_validation_allowed_actions,
    set_validation_status,
    check_validation_allowed,
)
from caerp.compute.math_utils import (
    compute_ht_from_ttc,
    floor,
)
from caerp.forms.supply import get_add_edit_line_schema
from caerp.forms.third_party.supplier import get_company_suppliers_from_request
from caerp.models.expense.types import ExpenseType
from caerp.models.node import Node
from caerp.models.supply import (
    SupplierInvoiceLine,
    SupplierOrder,
    SupplierOrderLine,
)
from caerp.models.tva import Tva
from caerp.utils.rest.apiv1 import RestError
from caerp.views import BaseRestView
from caerp.views.status import StatusView
from caerp.views.status.rest_api import (
    StatusLogEntryRestView,
    get_other_users_for_notification,
)
from caerp.views.status.utils import get_visibility_options

from .utils import get_supplier_doc_url

logger = logging.getLogger(__name__)


class BaseRestSupplierDocumentView(BaseRestView):
    """
    Factorize what is common among RestSupplierInvoiceView and
    RestSupplierOrderView
    """

    def get_delete_route(self):
        return get_supplier_doc_url(
            self.request,
            _query=dict(action="delete"),
        )

    def get_duplicate_route(self):
        return get_supplier_doc_url(
            self.request,
            _query=dict(action="duplicate"),
        )

    def _get_other_actions(self):
        raise NotImplementedError

    def _get_form_sections(self):
        raise NotImplementedError

    def post_format(self, entry, edit, attributes):
        """
        Add the company and user id after  add
        """
        if not edit:
            entry.company_id = self.context.id
            entry.user_id = self.request.identity.id
        return entry

    def form_config(self):
        """
        Form display options

        :returns: The sections that the end user can edit, the options
        available for the different select boxes
        """
        result = {
            "actions": {
                "main": self._get_status_actions(),
                "more": self._get_other_actions(),
            },
            "sections": self._get_form_sections(),
        }
        result = self._add_form_options(result)
        return result

    def _get_status_actions(self):
        """
        Returned datas describing available actions on the current item
        :returns: List of actions
        :rtype: list of dict
        """
        actions = []
        url = self.request.current_route_path(_query={"action": "validation_status"})
        for action in get_validation_allowed_actions(self.request, self.context):
            json_resp = action.__json__(self.request)
            json_resp["url"] = url
            json_resp["widget"] = "status"
            actions.append(json_resp)
        return actions

    def _delete_btn(self):
        """
        Return a deletion btn description

        :rtype: dict
        """
        url = self.get_delete_route()
        type_label = self.context.type_label.lower()
        return {
            "widget": "POSTButton",
            "option": {
                "url": url,
                "title": f"Supprimer définitivement cette {type_label}",
                "css": "icon only negative",
                "icon": "trash-alt",
                "confirm_msg": f"Êtes-vous sûr de vouloir supprimer cette {type_label} ?",
            },
        }

    def _duplicate_btn(self):
        """
        Return a duplicate btn description

        :rtype: dict
        """
        url = self.get_duplicate_route()
        type_label = self.context.type_label.lower()
        return {
            "widget": "POSTButton",
            "option": {
                "url": url,
                "title": f"Créer une nouvelle {type_label} à partir de celle-ci",
                "css": "btn icon only",
                "icon": "copy",
            },
        }

    def _get_purchase_types_options(self):
        query = ExpenseTypeQueryService.purchase_options(
            self.context.internal, self.context.lines
        )
        return self.dbsession.execute(query).scalars().all()

    def _get_suppliers_options(self):
        query = get_company_suppliers_from_request(self.request)
        result = [{"label": supplier.name, "value": supplier.id} for supplier in query]
        return result

    def _add_form_options(self, form_config):
        """
        add form options to the current configuration
        """
        options = {}

        options["today"] = datetime.date.today()
        options["purchase_types"] = self._get_purchase_types_options()
        options["csrf_token"] = get_csrf_token(self.request)

        options["company_customers_url"] = self.request.route_path(
            "/api/v1/companies/{id}/customers",
            id=self.context.company.id,
        )
        options["company_projects_url"] = self.request.route_path(
            "/api/v1/companies/{id}/projects",
            id=self.context.company.id,
        )
        options["company_businesses_url"] = self.request.route_path(
            "/api/v1/companies/{id}/businesses",
            id=self.context.company.id,
        )
        # Pour les mémos
        options["visibilities"] = get_visibility_options(self.request)
        options["notification_recipients"] = get_other_users_for_notification(
            self.request, self.context
        )
        form_config["options"] = options
        return form_config

    def get_writable_instances(self):
        Model = self.model_class
        query = Model.query().filter(Model.company_id == self.context.company_id)

        query = query.filter(
            Model.type_.notin_(("internalsupplier_invoice", "internalsupplier_order"))
        )
        query = query.filter(Model.status.in_(["draft", "invalid"]))
        query = query.order_by(
            Model.created_at.desc(),
        )
        return query


class BaseRestLineView(BaseRestView):
    """
    Logic is shared between SupplierOrderLine and SupplierInvoiceLine

    Subclass must define class attrs :

    - model_class
    - fk_field_to_container
    - duplicate_permission : the duplicate permission for destination container
        instance.
    """

    model_class = None
    duplicate_permission = None
    fk_field_to_container = ""

    def _get_current_document(self):
        if isinstance(self.context, Node):
            return self.context
        elif isinstance(self.context, SupplierOrderLine):
            return self.context.supplier_order
        elif isinstance(self.context, SupplierInvoiceLine):
            return self.context.supplier_invoice
        else:
            raise KeyError("On ne devrait pas arriver ici")

    def get_schema(self, submitted):
        document = self._get_current_document()
        return get_add_edit_line_schema(self.model_class, document.internal)

    def collection_get(self):
        return self.context.lines

    def post_format(self, entry, edit, attributes):
        """
        Associate a newly created line to current container
        """
        if not edit:
            setattr(entry, self.fk_field_to_container, self.context.id)
            entry.expense_type = ExpenseType.get(entry.type_id)

        if entry.expense_type.tva_on_margin:
            logger.info("Re-computing line amounts for TVA on margin")
            try:
                tva_value = Tva.get_default().value
            except AttributeError:
                tva_value = 2000  # integer format of 20%
            ttc = entry.ht + entry.tva
            entry.ht = floor(compute_ht_from_ttc(ttc, tva_value))
            entry.tva = ttc - entry.ht

        return entry

    def duplicate(self):
        """
        Duplicate line to an existing container of same type as context.
        """
        logger.info("Duplicate {}".format(self.model_class))
        container_id = self.request.json_body.get(self.fk_field_to_container)

        if container_id is None:
            return RestError(["Wrong {}".format(self.fk_field_to_container)])

        # Permission for source object is handled though add_view predicate
        dest_obj = SupplierOrder.get(container_id)
        if not self.request.has_permission(self.duplicate_permission, dest_obj):
            logger.error("Unauthorized action : possible break in attempt")
            raise HTTPForbidden()

        duplicate_kwargs = {self.fk_field_to_container: container_id}
        new_line = self.context.duplicate(**duplicate_kwargs)
        self.request.dbsession.add(new_line)
        self.request.dbsession.flush()
        return new_line


# raise Exception(
#     """
#     On en est ici dans le refactor Il reste les supply, tester un peu plus
#     Et refactorer le check_allowed_status (qui devrait relever de la valdiation)
#     du model SupplierInvoice
#     Ajouter des paid states managers sur les SupplierInvoice
# """
# )


class BaseSupplierValidationStatusView(StatusView):
    validation_function = None

    def check_allowed(self, status):
        check_validation_allowed(self.request, self.context, status)

    def status_process(self, status, params):
        return set_validation_status(self.request, self.context, status, **params)

    def validate(self):
        if self.validation_function is not None:
            try:
                f = self.validation_function
                f(self.context, self.request)
            except colander.Invalid as err:
                logger.exception(
                    "An error occured when validating this Invoice (id:%s)"
                    % (self.request.context.id)
                )
                raise err
        return {}

    def pre_status_process(self, status, params):
        if "comment" in params:
            self.context.status_comment = params["comment"]
        return StatusView.pre_status_process(self, status, params)

    def pre_wait_process(self, status, params):
        """
        Launched before the wait status is set

        :param str status: The new status that should be affected
        :param dict params: The params that were transmitted by the associated
        State's callback
        """
        self.validate()
        return {}

    def pre_valid_process(self, status, params):
        """
        Launched before the valid status is set

        :param str status: The new status that should be affected
        :param dict params: The params that were transmitted by the associated
        State's callback
        """
        self.validate()
        return {}


class SupplierStatusLogEntryRestView(StatusLogEntryRestView):
    def get_node_url(self, node):
        return get_supplier_doc_url(self.request, doc=node)

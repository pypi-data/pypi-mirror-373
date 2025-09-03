import datetime
import logging
import traceback

import colander
from pyramid.csrf import get_csrf_token
from pyramid.httpexceptions import HTTPForbidden
from sqlalchemy.orm.query import Query

from caerp.compute.math_utils import compute_ht_from_ttc, floor
from caerp.consts.permissions import PERMISSIONS
from caerp.controllers.expense_types import ExpenseTypeQueryService
from caerp.controllers.state_managers import (
    check_justified_allowed,
    check_validation_allowed,
    get_justified_allowed_actions,
    get_validation_allowed_actions,
    set_justified_status,
)
from caerp.forms.expense import (
    BookMarkSchema,
    get_add_edit_line_schema,
    get_add_edit_sheet_schema,
)
from caerp.models.company import Company
from caerp.models.expense.sheet import ExpenseKmLine, ExpenseLine, ExpenseSheet
from caerp.models.expense.types import ExpenseType
from caerp.models.sepa import BaseSepaWaitingPayment
from caerp.models.status import StatusLogEntry
from caerp.models.third_party import Supplier
from caerp.models.tva import Tva
from caerp.utils import strings
from caerp.utils.rest.apiv1 import Apiv1Resp, RestError
from caerp.views import BaseRestView, BaseView
from caerp.views.expenses.bookmarks import BookMarkHandler, get_bookmarks
from caerp.views.expenses.routes import (
    EXPENSE_BOOKMARK_API_ROUTE,
    EXPENSE_BOOKMARK_ITEM_API_ROUTE,
    EXPENSE_ITEM_API_ROUTE,
    EXPENSE_KMLINE_API_ROUTE,
    EXPENSE_KMLINE_ITEM_API_ROUTE,
    EXPENSE_LINE_ITEM_API_ROUTE,
    EXPENSE_LINES_API_ROUTE,
    EXPENSE_STATUS_LOG_ITEM_ROUTE,
    EXPENSE_STATUS_LOG_ROUTE,
)
from caerp.views.sepa.routes import SEPA_WAITING_PAYMENT_ITEM_ROUTE
from caerp.views.status import StatusView
from caerp.views.status.rest_api import (
    StatusLogEntryRestView,
    get_other_users_for_notification,
)
from caerp.views.status.utils import get_visibility_options

logger = logging.getLogger(__name__)


def _get_valid_duplicate_targets(
    source_sheet: ExpenseSheet, including_me=True
) -> Query:
    """
    :returns: valid targets for a duplicate of a line from source_sheet.
    """
    all_expenses = ExpenseSheet.query().filter_by(user_id=source_sheet.user_id)
    all_expenses = all_expenses.filter_by(company_id=source_sheet.company_id)
    if not including_me:
        all_expenses = all_expenses.filter(ExpenseSheet.id != source_sheet.id)
    all_expenses = all_expenses.filter(ExpenseSheet.status.in_(["draft", "invalid"]))
    return all_expenses


class RestExpenseSheetView(BaseRestView):
    factory = ExpenseSheet

    def get_schema(self, submitted):
        """
        Return the schema for ExpenseSheet add

        :param dict submitted: The submitted datas
        :returns: A colander.Schema
        """
        return get_add_edit_sheet_schema()

    def post_format(self, entry, edit, attributes):
        """
        Add the company and user id after sheet add
        """
        if not edit:
            entry.company_id = self.context.id
            entry.user_id = self.request.identity.id
        return entry

    def form_config(self):
        """
        Form display options

        :returns: The sections that the end user can edit, the options
        available
        for the different select boxes
        """

        result = {
            "actions": {
                "main": self._get_status_actions(),
                "more": self._get_other_actions(),
            },
            "sections": self._get_form_sections(),
        }
        if self.request.has_permission(
            PERMISSIONS["context.set_justified_expensesheet"]
        ):
            result["actions"]["justify"] = self._get_justified_toggle()

        result = self._add_form_options(result)
        return result

    def _get_form_sections(self):
        """
        Construit les informations relatives à l'édition des lignes de dépenses
        """
        actions = ["bookmark", "duplicate"]
        # Cas 1 : on édite la ndd parce qu'elle est draft ou invalid
        if self.context.status in ["draft", "invalid"]:
            if self.request.has_permission(PERMISSIONS["context.edit_expensesheet"]):
                actions.extend(["edit", "delete"])
        # Cas 2 : En attente de validation : justify + delete + edit
        elif self.context.status == "wait":
            if self.request.has_permission(
                PERMISSIONS["context.set_justified_expensesheet"]
            ):
                actions.extend(["justify", "delete"])
            if self.request.has_permission(PERMISSIONS["context.edit_expensesheet"]):
                actions.append("edit")
        # Cas 3 : Validée : justify uniquement
        else:
            if self.request.has_permission(
                PERMISSIONS["context.set_justified_expensesheet"]
            ):
                actions.append("justify")

        return {"general": {"line_actions": actions}}

    def _get_status_actions(self):
        """
        Returned datas describing available actions on the current item
        :returns: List of actions
        :rtype: list of dict
        """
        actions = []
        url = self.request.current_route_path(_query={"action": "status"})
        for action in get_validation_allowed_actions(self.request, self.context):
            json_resp = action.__json__(self.request)
            json_resp["url"] = url
            json_resp["widget"] = "status"
            actions.append(json_resp)
        if self.request.has_permission(PERMISSIONS["context.add_to_sepa_expensesheet"]):
            action = {
                "widget": "anchor",
                "option": {
                    "url": self.request.route_path(
                        "/expenses/{id}/add_to_sepa",
                        id=self.context.id,
                    ),
                    "label": "Mettre en paiement",
                    "title": (
                        "Marquer cette note de dépenses comme « À payer » afin"
                        " de l’inclure dans un ordre de virement SEPA"
                    ),
                    "css": "btn btn-primary",
                    "icon": "euro-sign",
                },
            }
            actions.append(action)
        elif self.context.has_waiting_payment():
            waiting_payment = self.context.get_waiting_payment()
            action = {
                "widget": "POSTButton",
                "option": {
                    "url": self.request.route_path(
                        SEPA_WAITING_PAYMENT_ITEM_ROUTE,
                        id=waiting_payment.id,
                    ),
                    "label": "Annuler la mise en paiement",
                    "title": "Cette note de dépenses ne sera plus marquée comme « À payer »",
                    "css": "btn negative",
                    "icon": "euro-slash",
                },
            }
            actions.append(action)
        return actions

    def _get_other_actions(self):
        """
        Return the description of other available actions :
            duplicate
            ...
        """
        result = []

        if self.request.has_permission(PERMISSIONS["context.add_payment_expensesheet"]):
            url = self.request.route_path(
                "/expenses/{id}/addpayment",
                id=self.context.id,
            )
            result.append(
                {
                    "widget": "anchor",
                    "option": {
                        "url": url,
                        "title": (
                            "Enregistrer un paiement pour cette note " "de dépenses"
                        ),
                        "css": "btn icon only",
                        "icon": "euro-circle",
                    },
                }
            )

        if self.request.has_permission(
            PERMISSIONS["context.edit_expensesheet"]
        ) and self.context.status in (
            "draft",
            "invalid",
        ):
            result.append(self._edit_btn())
        if self.request.has_permission(PERMISSIONS["company.view"]):
            result.append(self._duplicate_btn())
        result.append(self._print_btn())
        result.append(self._xls_btn())
        if self.context.status == "valid" and self.context.files:
            result.append(self._zip_btn())

        if self.request.has_permission(PERMISSIONS["context.delete_expensesheet"]):
            result.append(self._delete_btn())
        return result

    def _delete_btn(self):
        """
        Return a deletion btn description

        :rtype: dict
        """
        url = self.request.route_path("/expenses/{id}/delete", id=self.context.id)
        return {
            "widget": "POSTButton",
            "option": {
                "url": url,
                "title": "Supprimer définitivement ce document",
                "css": "btn icon only negative",
                "icon": "trash-alt",
                "confirm_msg": ("Êtes-vous sûr de vouloir supprimer cet élément ?"),
            },
        }

    def _print_btn(self):
        """
        Return a print btn for frontend printing
        """
        return {
            "widget": "button",
            "option": {
                "title": "Imprimer",
                "css": "btn icon only",
                "onclick": "window.print()",
                "icon": "print",
            },
        }

    def _xls_btn(self):
        """
        Return a button for xls rendering

        :rtype: dict
        """
        url = self.request.route_path("/expenses/{id}.xlsx", id=self.context.id)
        return {
            "widget": "anchor",
            "option": {
                "url": url,
                "title": "Export au format Excel (xlsx)",
                "css": "btn icon only",
                "icon": "file-excel",
            },
        }

    def _zip_btn(self):
        """ """
        url = self.request.route_path("/expenses/{id}.zip", id=self.context.id)
        return {
            "widget": "anchor",
            "option": {
                "url": url,
                "title": "Télécharger l'ensemble des justificatifs au format .zip",
                "css": "btn icon only",
                "icon": "download",
                "popup": True,
            },
        }

    def _duplicate_btn(self):
        """
        Return a duplicate btn description

        :rtype: dict
        """
        url = self.request.route_path("/expenses/{id}/duplicate", id=self.context.id)
        return {
            "widget": "anchor",
            "option": {
                "url": url,
                "title": ("Créer une nouvelle note de dépenses à partir de celle-ci"),
                "css": "btn icon only",
                "icon": "copy",
            },
        }

    def _edit_btn(self):
        """
        Return an edit btn description

        :rtype: dict
        """
        url = self.request.route_path("/expenses/{id}/edit", id=self.context.id)
        return {
            "widget": "anchor",
            "option": {
                "url": url,
                "title": (
                    "Modifier les informations (mois, année, et titre) de cette note de dépenses"
                ),
                "css": "btn icon only",
                "icon": "pen",
            },
        }

    def _get_justified_toggle(self):
        """
        Return a justification toggle button description

        :rtype: dict
        """
        url = self.request.route_path(
            "/api/v1/expenses/{id}",
            id=self.context.id,
            _query={"action": "justified_status"},
        )
        actions = get_justified_allowed_actions(self.request, self.context)

        return {
            "widget": "toggle",
            "options": {
                "url": url,
                "name": "justified",
                "current_value": self.context.get_lines_justified_status(),  # True/False/None
                "label": "Justificatifs",
                "toggle_label": "Changer le statut de tous les justificatifs en",
                "buttons": actions,
                "css": "btn",
            },
        }
        return

    def _add_form_options(self, form_config):
        """
        add form options to the current configuration
        """
        options = self._get_type_options()

        options["categories"] = [
            {
                "value": "1",
                "label": "Frais généraux",
                "description": ("Dépenses liées au fonctionnement de votre enseigne"),
            },
            {
                "value": "2",
                "label": "Achats client",
                "description": (
                    "Dépenses concernant directement votre activité     auprès"
                    " de vos clients"
                ),
            },
        ]

        options["bookmarks"] = get_bookmarks(self.request)

        options["expenses"] = self._get_existing_expenses_options()
        options["suppliers"] = self._get_suppliers_options()

        expense_sheet = self.request.context
        month = expense_sheet.month
        year = expense_sheet.year

        date = datetime.date(year, month, 1)
        options["today"] = date
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
        options["csrf_token"] = get_csrf_token(self.request)
        options["visibilities"] = get_visibility_options(self.request)
        options["notification_recipients"] = get_other_users_for_notification(
            self.request, self.context
        )

        form_config["options"] = options
        return form_config

    def _get_suppliers_options(self):
        assert isinstance(self.context, ExpenseSheet)

        query = Supplier.label_query()
        query = query.filter_by(
            company_id=self.context.company_id,
            archived=False,
        )

        return [
            {"label": supplier.label, "value": supplier.id} for supplier in query.all()
        ]

    def _get_type_options(self):
        expense_query = ExpenseTypeQueryService.expense_options(self.context.lines)
        purchase_query = ExpenseTypeQueryService.purchase_options(
            False, self.context.lines
        )
        km_query = ExpenseTypeQueryService.expensekm_options(
            self.context.user,
            self.context.year,
            self.context.lines,
            self.context.kmlines,
        )

        options = {
            "expense_types": self.dbsession.execute(
                expense_query.where(ExpenseType.type == "expense")
            )
            .scalars()
            .all(),
            "purchase_types": self.dbsession.execute(purchase_query).scalars().all(),
            "expensetel_types": self.dbsession.execute(
                expense_query.where(ExpenseType.type == "expensetel")
            )
            .scalars()
            .all(),
            "expensekm_types": self.dbsession.execute(km_query).scalars().all(),
        }
        return options

    def _get_existing_expenses_options(self):
        """
        Return existing expenses available for expense line duplication
        """
        result = []
        if self.context.status in ("draft", "invalid"):
            # On s'assure que la note courante soit dedans
            result.append(
                {
                    "label": "{month_label} / {year} (note courante)".format(
                        month_label=strings.month_name(self.context.month),
                        year=self.context.year,
                    ),
                    "id": self.context.id,
                }
            )

        all_expenses = _get_valid_duplicate_targets(
            self.context,
            including_me=False,
        )
        all_expenses = all_expenses.order_by(ExpenseSheet.year.desc()).order_by(
            ExpenseSheet.month.desc()
        )
        result.extend(
            [
                {
                    "label": "{month_label} / {year}".format(
                        month_label=strings.month_name(e.month), year=e.year
                    ),
                    "id": e.id,
                }
                for e in all_expenses
            ]
        )
        return result


class RestExpenseLineView(BaseRestView):
    """
    Base rest view for expense line handling
    """

    def _get_current_sheet(self):
        if isinstance(self.context, ExpenseSheet):
            return self.context
        else:
            return self.context.sheet

    def get_schema(self, submitted):
        return get_add_edit_line_schema(ExpenseLine, self._get_current_sheet())

    def collection_get(self):
        return self.context.lines

    def post_format(self, entry, edit, attributes):
        """
        Associate a newly created element to the parent sheet
        """
        if not edit:
            entry.sheet = self.context
            entry.expense_type = ExpenseType.get(entry.type_id)

        if entry.expense_type.tva_on_margin:
            try:
                tva_value = Tva.get_default().value
            except AttributeError:
                tva_value = 2000  # integer format of 20%
            entry.ht = floor(compute_ht_from_ttc(entry.manual_ttc, tva_value))
            entry.tva = entry.manual_ttc - entry.ht
        else:
            entry.manual_ttc = 0

        if edit:
            self.unset_justified_on_edit(entry)

        return entry

    def unset_justified_on_edit(self, entry):
        can_justify = self.request.has_permission(
            PERMISSIONS["context.set_justified_expensesheet"],
            self.context,
        )
        if entry.justified and not can_justify:
            # It has been justified before, but it has just changed…
            entry.justified = False

    def duplicate(self):
        """
        Duplicate an expense line to an existing ExpenseSheet
        """
        logger.info("Duplicate ExpenseLine")
        sheet_id = self.request.json_body.get("sheet_id")
        # queries only among authorized expense sheets
        valid_sheets = _get_valid_duplicate_targets(self.context.sheet)
        sheet = valid_sheets.filter_by(id=sheet_id).first()

        if sheet is None:
            return HTTPForbidden()

        if not self.request.has_permission(
            PERMISSIONS["context.edit_expensesheet"], sheet
        ):
            logger.error("Unauthorized action : possible break in attempt")
            raise HTTPForbidden()

        new_line = self.context.duplicate(sheet=sheet)
        self.request.dbsession.add(new_line)
        self.request.dbsession.flush()
        return new_line


class RestExpenseKmLineView(BaseRestView):
    """
    Base rest view for expense line handling
    """

    def get_schema(self, submitted):
        schema = get_add_edit_line_schema(ExpenseKmLine)
        return schema

    def collection_get(self):
        return self.context.kmlines

    def post_format(self, entry, edit, attributes):
        """
        Associate a newly created element to the parent task
        """
        if not edit:
            entry.sheet = self.context
        return entry

    def after_flush(self, entry, edit, attributes):
        """
        Compute ht amount of the km line
        """
        if edit:
            state = "update"
        else:
            state = "add"
        entry.on_before_commit(self.request, state, attributes)
        return entry

    def duplicate(self):
        """
        Duplicate an expense line to an existing ExpenseSheet
        """
        logger.info("Duplicate ExpenseKmLine")
        sheet_id = self.request.json_body.get("sheet_id")
        sheet = ExpenseSheet.get(sheet_id)

        if sheet is None:
            logger.error("Unauthorized action : possible break in attempt")
            return HTTPForbidden()

        if not self.request.has_permission(
            PERMISSIONS["context.edit_expensesheet"], sheet
        ):
            logger.error("Unauthorized action : possible break in attempt")
            raise HTTPForbidden()

        new_line = self.context.duplicate(sheet=sheet)
        if new_line is None:
            return RestError(
                [
                    "Aucun type de dépense kilométrique correspondant n'a pu"
                    " être retrouvé sur l'année {0}".format(sheet.year)
                ],
                code=403,
            )

        new_line.sheet_id = sheet.id
        self.request.dbsession.add(new_line)
        self.request.dbsession.flush()
        return new_line


class RestBookMarkView(BaseView):
    """
    Json rest-api for expense bookmarks handling
    """

    _schema = BookMarkSchema()

    @property
    def schema(self):
        return self._schema.bind(request=self.request)

    def get(self):
        """
        Rest GET Method : get
        """
        return get_bookmarks(self.request)

    def post(self):
        """
        Rest POST method : add
        """
        logger.debug("In the bookmark edition")

        appstruct = self.request.json_body
        try:
            bookmark = self.schema.deserialize(appstruct)
        except colander.Invalid as err:
            traceback.print_exc()
            logger.exception("  - Error in posting bookmark")
            logger.exception(appstruct)
            raise RestError(err.asdict(), 400)
        handler = BookMarkHandler(self.request)
        bookmark = handler.store(bookmark)
        return bookmark

    def put(self):
        """
        Rest PUT method : edit
        """
        self.post()

    def delete(self):
        """
        Removes a bookmark
        """
        logger.debug("In the bookmark deletion view")

        handler = BookMarkHandler(self.request)

        # Retrieving the id from the request
        id_ = self.request.matchdict.get("id")

        bookmark = handler.delete(id_)

        # if None is returned => there was no bookmark with this id
        if bookmark is None:
            raise RestError({}, 404)
        else:
            return dict(status="success")


class RestExpenseSheetStatusView(StatusView):
    def get_redirect_url(self):
        return self.request.route_path("/expenses/{id}", id=self.context.id)

    def check_allowed(self, status):
        check_validation_allowed(self.request, self.context, status)

    def pre_status_process(self, status, params):
        if "comment" in params:
            self.context.status_comment = params["comment"]
        return StatusView.pre_status_process(self, status, params)


class RestExpenseJustifiedStatusView(StatusView):
    """
    Common between Line / Sheet
    """

    def check_allowed(self, status):
        check_justified_allowed(self.request, self.context, status)

    def redirect(self):
        return Apiv1Resp(self.request, {"justified": self.context.justified})

    def status_process(self, status, params):
        return set_justified_status(self.request, self.context, status, **params)


class RestExpenseLineJustifiedStatusView(RestExpenseJustifiedStatusView):
    def post_status_process(self, status, params):
        # sync sheet if required
        sheet = self.context.sheet
        lines_justified_status = sheet.get_lines_justified_status()
        if lines_justified_status != sheet.justified:
            if lines_justified_status is None:
                sheet.justified = False
            else:
                set_justified_status(self.request, sheet, status, **params)
            self.dbsession.merge(sheet)


class RestExpenseSheetJustifiedStatusView(RestExpenseJustifiedStatusView):
    def post_status_process(self, status, params):
        # syncs lines
        for line in self.context.lines:
            line.justified = self.context.justified
            self.dbsession.merge(self.context)


class ExpenseStatusLogEntry(StatusLogEntryRestView):
    def get_node_url(self, node):
        return self.request.route_path("/expenses/{id}", id=node.id)


# def add_routes(config):
#     """
#     Add module's related routes
#    """
# config.add_route("/api/v1/bookmarks/{id}", r"/api/v1/bookmarks/{id:\d+}")
# config.add_route("/api/v1/bookmarks", "/api/v1/bookmarks")
# config.add_route(
#     "/api/v1/expenses",
#     "/api/v1/expenses",
# )

# config.add_route(
#     "/api/v1/expenses/{id}",
#     r"/api/v1/expenses/{id:\d+}",
#     traverse="/expenses/{id}",
# )

# config.add_route(
#     "/api/v1/expenses/{id}/lines",
#     "/api/v1/expenses/{id}/lines",
#     traverse="/expenses/{id}",
# )

# config.add_route(
#     "/api/v1/expenses/{id}/lines/{lid}",
#     r"/api/v1/expenses/{id:\d+}/lines/{lid:\d+}",
#     traverse="/expenselines/{lid}",
# )

# config.add_route(
#     "/api/v1/expenses/{id}/kmlines",
#     r"/api/v1/expenses/{id:\d+}/kmlines",
#     traverse="/expenses/{id}",
# )

# config.add_route(
#     "/api/v1/expenses/{id}/kmlines/{lid}",
#     r"/api/v1/expenses/{id:\d+}/kmlines/{lid:\d+}",
#     traverse="/expenselines/{lid}",
# )

# config.add_route(
#     "/api/v1/expenses/{id}/statuslogentries",
#     r"/api/v1/expenses/{id:\d+}/statuslogentries",
#     traverse="/expenses/{id}",
# )

# config.add_route(
#     "/api/v1/expenses/{eid}/statuslogentries/{id}",
#     r"/api/v1/expenses/{eid:\d+}/statuslogentries/{id:\d+}",
#     traverse="/statuslogentries/{id}",
# )


def includeme(config):
    """
    Add rest api views
    """
    config.add_rest_service(
        RestExpenseSheetView,
        EXPENSE_ITEM_API_ROUTE,
        collection_route_name="/api/v1/expenses",
        view_rights=PERMISSIONS["company.view"],
        add_rights=PERMISSIONS["context.add_expensesheet"],
        edit_rights=PERMISSIONS["context.edit_expensesheet"],
        delete_rights=PERMISSIONS["context.delete_expensesheet"],
        collection_view_rights=PERMISSIONS["company.view"],
        collection_context=Company,
        context=ExpenseSheet,
    )

    # Form configuration view
    config.add_view(
        RestExpenseSheetView,
        attr="form_config",
        route_name=EXPENSE_ITEM_API_ROUTE,
        renderer="json",
        request_param="form_config",
        permission=PERMISSIONS["company.view"],
        context=ExpenseSheet,
    )

    # Status view
    config.add_view(
        RestExpenseSheetStatusView,
        route_name=EXPENSE_ITEM_API_ROUTE,
        request_param="action=status",
        permission=PERMISSIONS["company.view"],
        request_method="POST",
        renderer="json",
        context=ExpenseSheet,
    )

    # Status view
    config.add_view(
        RestExpenseSheetJustifiedStatusView,
        route_name=EXPENSE_ITEM_API_ROUTE,
        request_param="action=justified_status",
        permission=PERMISSIONS["company.view"],
        request_method="POST",
        renderer="json",
        context=ExpenseSheet,
    )

    # Line views
    config.add_rest_service(
        RestExpenseLineView,
        EXPENSE_LINE_ITEM_API_ROUTE,
        collection_route_name=EXPENSE_LINES_API_ROUTE,
        view_rights=PERMISSIONS["company.view"],
        add_rights=PERMISSIONS["context.edit_expensesheet"],
        edit_rights=PERMISSIONS["context.edit_expensesheet"],
        delete_rights=PERMISSIONS["context.edit_expensesheet"],
        collection_context=ExpenseSheet,
        context=ExpenseLine,
    )
    config.add_view(
        RestExpenseLineView,
        attr="duplicate",
        route_name=EXPENSE_LINE_ITEM_API_ROUTE,
        request_param="action=duplicate",
        # Les droits d'edit concernent la destination donc sont traités dans
        # la view elle-même
        permission=PERMISSIONS["company.view"],
        request_method="POST",
        renderer="json",
        context=ExpenseLine,
    )
    # Status view
    config.add_view(
        RestExpenseLineJustifiedStatusView,
        route_name=EXPENSE_LINE_ITEM_API_ROUTE,
        request_param="action=justified_status",
        permission=PERMISSIONS["context.set_justified_expensesheet"],
        request_method="POST",
        renderer="json",
        context=ExpenseLine,
    )

    # Km Line views
    config.add_rest_service(
        RestExpenseKmLineView,
        EXPENSE_KMLINE_ITEM_API_ROUTE,
        collection_route_name=EXPENSE_KMLINE_API_ROUTE,
        view_rights=PERMISSIONS["company.view"],
        add_rights=PERMISSIONS["context.edit_expensesheet"],
        edit_rights=PERMISSIONS["context.edit_expensesheet"],
        delete_rights=PERMISSIONS["context.edit_expensesheet"],
        collection_context=ExpenseSheet,
        context=ExpenseKmLine,
    )
    config.add_view(
        RestExpenseKmLineView,
        attr="duplicate",
        route_name=EXPENSE_KMLINE_ITEM_API_ROUTE,
        request_param="action=duplicate",
        permission=PERMISSIONS["company.view"],
        request_method="POST",
        renderer="json",
        context=ExpenseKmLine,
    )
    # BookMarks
    config.add_rest_service(
        RestBookMarkView,
        EXPENSE_BOOKMARK_ITEM_API_ROUTE,
        collection_route_name=EXPENSE_BOOKMARK_API_ROUTE,
        view_rights=PERMISSIONS["global.authenticated"],
        add_rights=PERMISSIONS["global.authenticated"],
        edit_rights=PERMISSIONS["global.authenticated"],
        delete_rights=PERMISSIONS["global.authenticated"],
        collection_view_rights=PERMISSIONS["global.authenticated"],
    )

    config.add_rest_service(
        ExpenseStatusLogEntry,
        EXPENSE_STATUS_LOG_ITEM_ROUTE,
        collection_route_name=EXPENSE_STATUS_LOG_ROUTE,
        collection_view_rights=PERMISSIONS["company.view"],
        add_rights=PERMISSIONS["company.view"],
        view_rights=PERMISSIONS["context.view_statuslogentry"],
        edit_rights=PERMISSIONS["context.edit_statuslogentry"],
        delete_rights=PERMISSIONS["context.delete_statuslogentry"],
        collection_context=ExpenseSheet,
        context=StatusLogEntry,
    )

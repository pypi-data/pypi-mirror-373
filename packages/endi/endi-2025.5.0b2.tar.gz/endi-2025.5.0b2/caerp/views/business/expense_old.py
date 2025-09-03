"""
OBSOLÈTE
--------

Replacé par l'utilisation du panel 'linked_expenses'.

Ce fichier, ainsi que le template associé ('templates/business/expenses_hybrid.mako'), 
sont conservés au cas où l'association/dissociation d'achats directement depuis les 
fiches affaires / dossier / client soient réclamés par les utilisateurs.

"""

import colander
import deform
import itertools

from deform import Form
from pyramid.httpexceptions import HTTPFound
from pyramid_deform import CSRFSchema

from caerp.consts.permissions import PERMISSIONS
from caerp.exception import BadRequest
from caerp.forms.expense import ExpenseSeq
from caerp.forms.supply.supplier_invoice import SupplierInvoiceLineSeq
from caerp.models.expense.sheet import BaseExpenseLine
from caerp.models.project.business import Business
from caerp.models.supply.supplier_invoice import SupplierInvoiceLine
from caerp.utils.widgets import POSTButton
from caerp.views import (
    submit_btn,
    BaseView,
    BaseFormView,
    TreeMixin,
)
from caerp.views.business.routes import (
    BUSINESS_ITEM_EXPENSES_ROUTE,
    BUSINESS_ITEM_EXPENSES_UNLINK_ROUTE,
)
from caerp.views.project.project import ProjectEntryPointView


class ExpenseSelectionSchema(colander.MappingSchema):
    """
    Multi-selection Expense Line mapping schema
    """

    lines = ExpenseSeq(
        title="Sélectionner une ou plusieurs dépenses",
        widget=deform.widget.SequenceWidget(
            min_len=1,
            add_subitem_text_template="Ajouter une dépense",
        ),
    )
    csrf_token = CSRFSchema()["csrf_token"]


class SupplierInvoiceLineSelectionSchema(colander.MappingSchema):
    """
    Multi-selection SupplierInvoiceLine Mapping schema.
    """

    lines = SupplierInvoiceLineSeq(
        title="Sélectionner un ou plusieurs achats",
        widget=deform.widget.SequenceWidget(
            min_len=1,
            add_subitem_text_template=(
                "Ajouter une autre ligne de facture fournisseur"
            ),
        ),
    )
    csrf_token = CSRFSchema()["csrf_token"]


def get_link_form(request, context, entity, schema, counter=None):
    """
    :param entity: the entity we want to link to
    """
    _schema = schema().bind(request=request, context=context)
    submit_url = request.route_path(
        BUSINESS_ITEM_EXPENSES_ROUTE,
        id=context.id,
        _query=dict(action="link_{}".format(entity.__tablename__)),
    )
    form = Form(
        _schema,
        action=submit_url,
        buttons=(submit_btn,),
        counter=counter,
        formid="link_{}".format(entity.__tablename__),
    )
    return form


class AbstractLinkToLineView(BaseFormView):
    """
    Abstract view to link instances of some line-ish model to a Business
    The following properties must be defined by inheritor:

    - schema: the schema for model selection
    - model: the model class
    - success_msg_singular: the message to flash to the user after sucessfuly
      linking one line
    - success_msg_plural: the message to flash to the user after sucessfuly
      linking several lines
    """

    def submit_success(self, appstruct):
        business = self.context
        for line_id in appstruct["lines"]:
            line = self.model.get(line_id)
            line.link_to(business)
            self.dbsession.merge(line)

        if len(appstruct["lines"]) > 1:
            msg = self.success_msg_plural
        else:
            msg = self.success_msg_singular

        self.session.flash(msg)
        return self.redirect()

    def submit_failure(self, appstruct):
        self.session.flash(
            "Impossible de rattacher les lignes à l'affaire",
            "error",
        )
        return self.redirect()

    def redirect(self):
        return HTTPFound(
            self.request.route_path(
                BUSINESS_ITEM_EXPENSES_ROUTE,
                id=self.context.id,
            )
        )


def _type_keyword_to_class(_type):
    if _type == "supplier_invoice_line":
        return SupplierInvoiceLine
    elif _type == "base_expense_line":
        return BaseExpenseLine
    else:
        raise BadRequest("Wrong keyword {}".format(_type))


def _object_to_type_keyword(line):
    if isinstance(line, BaseExpenseLine):
        return "base_expense_line"
    elif isinstance(line, SupplierInvoiceLine):
        return "supplier_invoice_line"
    else:
        raise BadRequest("Wrong class {}".format(type(line)))


class UnlinkLineView(BaseView):
    def __call__(self):
        line_id = self.request.matchdict["line_id"]
        _type = self.request.matchdict["type"]

        klass = _type_keyword_to_class(_type)

        obj = klass.get(line_id)

        if obj and obj.business_id == self.context.id:
            obj.business_id = None
            obj.customer_id = None
            obj.project_id = None
            self.dbsession.merge(obj)

            self.session.flash(
                "La ligne a bien été détachée de cette affaire ; vous pouvez l'affecter à une autre affaire."
            )
            return self.redirect()
        else:
            raise BadRequest("Invalid linked line")

    def redirect(self):
        return HTTPFound(
            self.request.route_path(
                BUSINESS_ITEM_EXPENSES_ROUTE,
                id=self.context.id,
            )
        )


class LinkToSupplierInvoiceLineView(AbstractLinkToLineView):
    schema = SupplierInvoiceLineSelectionSchema()
    model = SupplierInvoiceLine
    success_msg_plural = "Les lignes ont bien été rattachées à l'affaire"
    success_msg_singular = "La ligne a bien été rattachée à l'affaire"


class LinkToExpenseView(AbstractLinkToLineView):
    schema = ExpenseSelectionSchema()
    model = BaseExpenseLine
    success_msg_plural = "Les dépenses ont bien été rattachées à l'affaire"
    success_msg_singular = "La dépense a bien été rattachée à l'affaire"


class BusinessExpensesHybridListView(BaseView, TreeMixin):
    """Lists both expenses and supplier invoices"""

    route_name = BUSINESS_ITEM_EXPENSES_ROUTE

    add_template_vars = (
        "title",
        "expense_lines",
        "supplier_invoice_lines",
        "link_to_expense_form",
        "link_to_supplier_invoice_line_form",
        "get_unlink_line_link",
    )

    @property
    def title(self):
        business = self.context
        return "Achats liés à l'affaire {}".format(business.name)

    def _get_supplier_invoice_lines(self):
        return SupplierInvoiceLine.query().filter_by(
            business_id=self.context.id,
        )

    def _get_expenses_lines(self):
        return BaseExpenseLine.query().filter_by(business_id=self.context.id)

    def _link_to_expense_form(self, counter):
        return get_link_form(
            schema=ExpenseSelectionSchema,
            entity=BaseExpenseLine,
            context=self.context,
            request=self.request,
            counter=counter,
        )

    def _link_to_supplier_invoice_line_form(self, counter):
        return get_link_form(
            schema=SupplierInvoiceLineSelectionSchema,
            entity=SupplierInvoiceLine,
            context=self.context,
            request=self.request,
            counter=counter,
        )

    def get_unlink_line_link(self, line):
        url = self.request.route_path(
            "/businesses/{id}/expenses/unlink/{type}/{line_id}",
            id=self.context.id,
            type=_object_to_type_keyword(line),
            line_id=line.id,
        )
        return POSTButton(
            label="",
            url=url,
            title="Détacher",
            icon="unlink",
        )

    def __call__(self):
        self.populate_navigation()
        counter = itertools.count()
        return dict(
            expense_lines=self._get_expenses_lines(),
            supplier_invoice_lines=self._get_supplier_invoice_lines(),
            title=self.title,
            link_to_expense_form=self._link_to_expense_form(counter),
            link_to_supplier_invoice_line_form=self._link_to_supplier_invoice_line_form(
                counter
            ),
            get_unlink_line_link=self.get_unlink_line_link,
        )


def includeme(config):
    config.add_tree_view(
        BusinessExpensesHybridListView,
        parent=ProjectEntryPointView,
        renderer="caerp:templates/business/expenses_hybrid.mako",
        permission=PERMISSIONS["company.view"],
        layout="business",
        context=Business,
    )
    config.add_view(
        LinkToSupplierInvoiceLineView,
        route_name=BUSINESS_ITEM_EXPENSES_ROUTE,
        request_param="action=link_supplier_invoice_line",
        permission=PERMISSIONS["company.view"],
        request_method="POST",
        require_csrf=True,
        context=Business,
    )
    config.add_view(
        LinkToExpenseView,
        route_name=BUSINESS_ITEM_EXPENSES_ROUTE,
        request_param="action=link_baseexpense_line",
        permission=PERMISSIONS["company.view"],
        request_method="POST",
        require_csrf=True,
        context=Business,
    )
    config.add_view(
        UnlinkLineView,
        route_name=BUSINESS_ITEM_EXPENSES_UNLINK_ROUTE,
        permission=PERMISSIONS["company.view"],
        request_method="POST",
        require_csrf=True,
        context=Business,
    )

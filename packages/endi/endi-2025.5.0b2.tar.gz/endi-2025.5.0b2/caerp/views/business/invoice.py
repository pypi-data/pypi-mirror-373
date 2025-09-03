import logging

from pyramid.httpexceptions import HTTPFound, HTTPForbidden

from caerp.consts.permissions import PERMISSIONS
from caerp.controllers.business import (
    gen_invoice_from_payment_deadline,
    gen_new_intermediate_invoice,
)
from caerp.services.business import (
    find_payment_deadline_by_id,
    get_sold_deadlines,
)
from caerp.forms.business.business import get_new_invoice_from_payment_deadline_schema
from caerp.forms.progress_invoicing import get_new_invoice_schema
from caerp.models.task import Task
from caerp.models.project.business import Business
from caerp.views import (
    TreeMixin,
    BaseFormView,
)
from caerp.views.business.routes import (
    BUSINESS_ITEM_INVOICE_ROUTE,
    BUSINESS_ITEM_INVOICE_EXPORT_ROUTE,
    BUSINESS_ITEM_INVOICING_ROUTE,
    BUSINESS_ITEM_PROGRESS_INVOICING_ROUTE,
)
from caerp.views.invoices.lists import (
    CompanyInvoicesListView,
    CompanyInvoicesCsvView,
    CompanyInvoicesXlsView,
    CompanyInvoicesOdsView,
    filter_all_status,
)
from caerp.views.project.project import ProjectEntryPointView


logger = logging.getLogger(__name__)

FIELDS_TO_EXCLUDE_FOR_LIST = (
    "year",
    "financial_year",
    "customer",
    "business_type",
)


class BusinessInvoicesListView(CompanyInvoicesListView, TreeMixin):
    """
    Invoice list for one given company
    """

    route_name = BUSINESS_ITEM_INVOICE_ROUTE

    add_template_vars = CompanyInvoicesListView.add_template_vars + ("add_links",)
    is_admin = False
    fields_to_exclude = FIELDS_TO_EXCLUDE_FOR_LIST

    @property
    def add_links(self):
        return []
        # return get_invoicing_links(self.context, self.request)

    def _get_company_id(self, appstruct):
        return self.request.context.project.company_id

    @property
    def title(self):
        return "Factures de l'affaire {0}".format(self.request.context.name)

    def filter_business(self, query, appstruct):
        self.populate_navigation()
        query = query.filter(Task.business_id == self.context.id)
        return query


class BusinessInvoicingView(BaseFormView):
    pass


class BusinessInvoicesCsvView(CompanyInvoicesCsvView):
    fields_to_exclude = FIELDS_TO_EXCLUDE_FOR_LIST

    def _get_company_id(self, appstruct):
        return self.request.context.project.company_id

    def filter_business(self, query, appstruct):
        logger.debug(" + Filtering by business_id")
        return query.filter(Task.business_id == self.context.id)

    filter_status = filter_all_status


class BusinessInvoicesXlsView(CompanyInvoicesXlsView):
    fields_to_exclude = FIELDS_TO_EXCLUDE_FOR_LIST

    def _get_company_id(self, appstruct):
        return self.request.context.project.company_id

    def filter_business(self, query, appstruct):
        logger.debug(" + Filtering by business_id")
        return query.filter(Task.business_id == self.context.id)

    filter_status = filter_all_status


class BusinessInvoicesOdsView(CompanyInvoicesOdsView):
    fields_to_exclude = FIELDS_TO_EXCLUDE_FOR_LIST

    def _get_company_id(self, appstruct):
        return self.request.context.project.company_id

    def filter_business(self, query, appstruct):
        logger.debug(" + Filtering by business_id")
        return query.filter(Task.business_id == self.context.id)

    filter_status = filter_all_status


# Facturation CLASSIQUE
def gen_invoice_from_payment_deadline_view(context, request):
    """
    Entry point for invoice generation based on a payment deadline

    Redirect to the view here above if the deadline is an intermdiary one
    Else produce the final sold invoice
    """
    deadline_id = request.matchdict["deadline_id"]

    deadline = find_payment_deadline_by_id(request, context, deadline_id)

    if deadline in get_sold_deadlines(request, context):
        invoice = gen_invoice_from_payment_deadline(request, context, deadline)
        return HTTPFound(
            request.route_path(
                "/invoices/{id}",
                id=invoice.id,
            )
        )
    else:
        return HTTPFound(
            request.current_route_path(
                _query={
                    "deadline_id": deadline_id,
                    "action": "details",
                }
            )
        )


class AddInvoiceFromPaymentDeadlineView(BaseFormView):
    """
    View for intermediate invoice generation
    Asks the user to choose if the details of the Estimation should
    be added to the new draft invoice

    :param obj request: The request object
    :param obj context: The current business
    """

    title = "Nouvelle facture"

    def before(self, form):
        appstruct = {"deadline_id": self.request.matchdict["deadline_id"]}
        form.set_appstruct(appstruct)

    def get_schema(self):
        return get_new_invoice_from_payment_deadline_schema()

    def submit_success(self, appstruct):
        deadline_id = appstruct["deadline_id"]
        add_estimation_details = appstruct.get("add_estimation_details", False)
        deadline = find_payment_deadline_by_id(self.request, self.context, deadline_id)

        if not deadline:
            invoice = gen_new_intermediate_invoice(
                self.request,
                self.context,
                add_estimation_details=add_estimation_details,
            )
        else:
            invoice = gen_invoice_from_payment_deadline(
                self.request,
                self.context,
                deadline,
                add_estimation_details=add_estimation_details,
            )
        return HTTPFound(
            self.request.route_path(
                "/invoices/{id}",
                id=invoice.id,
            )
        )


# Facturation À L'AVANCEMENT
class BusinessProgressInvoicingAddView(BaseFormView):
    """
    Specific invoice add view
    """

    title = "Nouvelle facture"
    schema = get_new_invoice_schema()

    def submit_success(self, appstruct):
        invoice = self.context.add_progress_invoicing_invoice(
            self.request, self.request.identity
        )
        invoice.name = appstruct.get("name")
        url = self.request.route_path("/invoices/{id}", id=invoice.id)
        return HTTPFound(url)


def gen_progress_sold_invoice_view(context, request):
    """
    Generate the final invoice

    :param obj request: The request object
    :param obj context: The current business
    """
    if context.invoicing_mode != context.PROGRESS_MODE:
        raise HTTPForbidden()
    else:
        invoice = context.add_progress_invoicing_sold_invoice(request, request.identity)
    return HTTPFound(
        request.route_path(
            "/invoices/{id}",
            id=invoice.id,
        )
    )


def includeme(config):
    config.add_tree_view(
        BusinessInvoicesListView,
        parent=ProjectEntryPointView,
        renderer="caerp:templates/business/invoices.mako",
        permission=PERMISSIONS["company.view"],
        layout="business",
        context=Business,
    )
    config.add_view(
        BusinessInvoicesCsvView,
        route_name=BUSINESS_ITEM_INVOICE_EXPORT_ROUTE,
        match_param="extension=csv",
        permission=PERMISSIONS["company.view"],
        context=Business,
    )

    config.add_view(
        BusinessInvoicesOdsView,
        route_name=BUSINESS_ITEM_INVOICE_EXPORT_ROUTE,
        match_param="extension=ods",
        permission=PERMISSIONS["company.view"],
        context=Business,
    )

    config.add_view(
        BusinessInvoicesXlsView,
        route_name=BUSINESS_ITEM_INVOICE_EXPORT_ROUTE,
        match_param="extension=xls",
        permission=PERMISSIONS["company.view"],
        context=Business,
    )
    config.add_view(
        gen_invoice_from_payment_deadline_view,
        route_name=BUSINESS_ITEM_INVOICING_ROUTE,
        permission=PERMISSIONS["context.add_invoice"],
        context=Business,
    )
    config.add_view(
        AddInvoiceFromPaymentDeadlineView,
        request_param="action=details",
        route_name=BUSINESS_ITEM_INVOICING_ROUTE,
        permission=PERMISSIONS["context.add_invoice"],
        renderer="caerp:templates/base/formpage.mako",
        context=Business,
    )
    config.add_view(
        gen_progress_sold_invoice_view,
        route_name=BUSINESS_ITEM_PROGRESS_INVOICING_ROUTE,
        permission=PERMISSIONS["context.add_invoice"],
        request_param="action=sold",
        layout="default",
        context=Business,
    )
    config.add_view(
        BusinessProgressInvoicingAddView,
        route_name=BUSINESS_ITEM_PROGRESS_INVOICING_ROUTE,
        layout="business",
        permission=PERMISSIONS["context.add_invoice"],
        renderer="caerp:templates/base/formpage.mako",
        context=Business,
    )

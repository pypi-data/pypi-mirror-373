"""
Rest views for invoices and cancelinvoices
"""
import os
import logging
import colander
from caerp.consts.permissions import PERMISSIONS
from caerp.controllers.state_managers.payment import check_node_resulted

from caerp.models.company import Company
from caerp.models.indicators import SaleFileRequirement
from caerp.models.task import (
    Invoice,
    CancelInvoice,
    DiscountLine,
    TaskLine,
    TaskLineGroup,
    PostTTCLine,
)
from caerp.models.status import StatusLogEntry
from caerp.forms.tasks.invoice import (
    validate_invoice,
    validate_cancelinvoice,
    get_add_edit_invoice_schema,
    get_add_edit_cancelinvoice_schema,
)

from caerp.views.project.routes import PROJECT_ITEM_INVOICE_ROUTE
from caerp.views.business.routes import BUSINESS_ITEM_INVOICE_ROUTE
from caerp.views.task.utils import get_task_url
from caerp.views.task.rest_api import (
    TaskAddRestView,
    TaskRestView,
    TaskLineGroupRestView,
    TaskLineRestView,
    DiscountLineRestView,
    PostTTCLineRestView,
    TaskFileRequirementRestView,
    TaskStatusLogEntryRestView,
    task_total_view,
    TaskFileRestView,
)

# from caerp.views.files.rest_api import FileRestView

from caerp.views.task.views import TaskStatusView
from caerp.views.task.utils import get_payment_conditions
from .routes import (
    API_CINV_FILES_ROUTE,
    API_INVOICE_ADD_ROUTE,
    API_CINV_ITEM_ROUTE,
    API_CINV_COLLECTION_ROUTE,
    API_INVOICE_COLLECTION_ROUTE,
    API_INVOICE_FILES_ROUTE,
    API_INVOICE_ITEM_ROUTE,
)

logger = logging.getLogger(__name__)


class InvoiceAddRestView(TaskAddRestView):
    """
    Invoice Add Rest View, Company is the current context

    .. http:get:: /api/v1/companies/(company_id)/invoices/add?form_config=1
        :noindex:

            Returns configuration informations for Invoice add form

        :query int: company_id (*required*) -- The id of the company

    .. http:post:: /api/v1/companies/(company_id)/invoices/add
        :noindex:

            Add a new invoice

        :query int: company_id (*required*) -- The if of the company
    """

    factory = Invoice


class InvoiceRestView(TaskRestView):
    factory = Invoice

    def get_schema(self, submitted):
        """
        Return the schema for Invoice add/edition

        :param dict submitted: The submitted datas
        :returns: A colander.Schema
        """
        excludes = ("status", "children", "parent", "business_type_id")
        return get_add_edit_invoice_schema(excludes=excludes)

    def _more_form_sections(self, sections):
        """
        Add invoice specific form sections to the sections returned to the
        end user

        :param dict sections: The sections to return
        :returns: The sections
        """
        sections["composition"]["classic"]["discounts"] = {"mode": "classic"}
        sections["payment_conditions"] = {"edit": True}

        if self.context.has_progress_invoicing_plan():
            composition = sections["composition"]
            composition["mode"] = "progress_invoicing"
            composition["progress_invoicing"] = {}
            # Factures de situation
            sections["display_options"]["input_mode_edit"] = False
            composition.pop("discounts", False)

        elif (
            self.context.business.invoicing_mode == self.context.business.PROGRESS_MODE
        ):
            composition = sections["composition"]["classic"]
            # Cas des factures d'acompte
            # composition["lines"]["quantity"]["edit"] = False
            # composition["lines"]["cost"]["edit"] = False
            composition["lines"]["tva"]["edit"] = False
            # composition["lines"]["can_add"] = False
            # composition["lines"]["can_delete"] = False
        else:
            sections["composition"]["classic"]["post_ttc_lines"] = {}

        if (
            "insurance_id" in sections["common"]
            and self.context.estimation_id
            and self.context.insurance_id
        ):
            sections["common"]["edit"] = False

        if self.context.estimation_id:
            # Pas de changement de mode de saisie si on a un devis à la source
            sections["display_options"]["input_mode_edit"] = False

        return sections

    def _more_form_options(self, form_options):
        """
        Add invoice specific form options to the options returned to the end
        user

        :param dict form_options: The options returned to the end user
        :returns: The form_options with new elements
        """
        form_options.update(
            {
                "payment_conditions": get_payment_conditions(self.request),
                "allow_unchronological_invoice_sequence": self.request.config.get_value(
                    "allow_unchronological_invoice_sequence", False, bool
                ),
            }
        )
        return form_options

    def post_format(self, entry, edit, attributes):
        if edit:
            if "date" in attributes and "financial_year" not in attributes:
                if attributes["date"].year != entry.financial_year:
                    entry.financial_year = attributes["date"].year
        return entry

    def related_estimation(self):
        """
        Collect data about a related estimation(s)
        """
        result = []
        if self.context.estimation_id:
            estimation = self.context.estimation
            result.append(
                {
                    "id": estimation.id,
                    "label": "{} {}".format(
                        estimation.name, estimation.get_short_internal_number()
                    ),
                    "url": get_task_url(self.request, estimation),
                }
            )
        elif self.context.business.invoicing_mode == "progress":
            for estimation in self.context.business.estimations:
                result.append(
                    {
                        "id": estimation.id,
                        "label": "{} {}".format(
                            estimation.name, estimation.get_short_internal_number()
                        ),
                        "url": get_task_url(self.request, estimation),
                    }
                )
        return result


class CancelInvoiceRestView(TaskRestView):
    factory = CancelInvoice

    def get_schema(self, submitted):
        """
        Return the schema for CancelInvoice add/edition

        :param dict submitted: The submitted datas
        :returns: A colander.Schema
        """
        excludes = (
            "status",
            "children",
            "parent",
        )
        return get_add_edit_cancelinvoice_schema(excludes=excludes)

    def _more_form_options(self, options):
        """
        Update form options to add the info that we edit a CancelInvoice
        """
        options["is_cancelinvoice"] = True
        options["cancel_resulted_invoice"] = self.context.invoice.is_resulted()
        options[
            "allow_unchronological_invoice_sequence"
        ] = self.request.config.get_value(
            "allow_unchronological_invoice_sequence", False, bool
        )
        return options

    def _more_form_sections(self, sections):
        """
        Update form sections to set cancelinvoice specific rights

        :param dict sections: The sections to return
        :returns: The sections
        """
        if self.context.invoicing_mode == self.context.PROGRESS_MODE:
            composition = sections["composition"]
            composition["mode"] = "progress_invoicing"
            composition["progress_invoicing"] = {}
            sections["display_options"]["input_mode_edit"] = False
        return sections


class InvoiceStatusRestView(TaskStatusView):
    validation_function = staticmethod(validate_invoice)
    state_manager_key = "status"

    def get_parent_url(self):
        if self.context.business.visible:
            business_id = self.context.business_id
            result = self.request.route_path(
                BUSINESS_ITEM_INVOICE_ROUTE, id=business_id
            )
        else:
            project_id = self.context.project_id
            result = self.request.route_path(PROJECT_ITEM_INVOICE_ROUTE, id=project_id)
        return result

    def validate(self):
        try:
            f = self.validation_function
            f(self.context, self.request)
        except colander.Invalid as err:
            logger.exception(f"An error occured when validating {self.request.context}")
            raise err
        return {}


class CancelInvoiceStatusRestView(InvoiceStatusRestView):
    validation_function = staticmethod(validate_cancelinvoice)
    state_manager_key = "status"

    def post_valid_process(self, status, params):
        TaskStatusView.post_valid_process(self, status, params)
        check_node_resulted(self.request, self.context.invoice)
        self.context.invoice.historize_paid_status(self.request.identity)


def add_invoice_routes(config):
    """
    Add invoice rest related routes to the current configuration

    :param obj config: Pyramid config object
    """
    for collection in (
        "task_line_groups",
        "discount_lines",
        "post_ttc_lines",
        "file_requirements",
        "total",
    ):
        route = os.path.join(API_INVOICE_ITEM_ROUTE, collection)
        config.add_route(route, route, traverse="/tasks/{id}")

    FILE_REQ_ITEM_ROUTE = os.path.join(
        API_INVOICE_COLLECTION_ROUTE, "{eid}", "file_requirements", "{id}"
    )
    config.add_route(
        FILE_REQ_ITEM_ROUTE,
        FILE_REQ_ITEM_ROUTE,
        traverse="/indicators/{id}",
    )

    config.add_route(
        "/api/v1/invoices/{eid}/task_line_groups/{id}",
        r"/api/v1/invoices/{eid}/task_line_groups/{id:\d+}",
        traverse="/task_line_groups/{id}",
    )
    config.add_route(
        "/api/v1/invoices/{eid}/task_line_groups/{id}/task_lines",
        r"/api/v1/invoices/{eid}/task_line_groups/{id:\d+}/task_lines",
        traverse="/task_line_groups/{id}",
    )
    config.add_route(
        "/api/v1/invoices/{eid}/task_line_groups/{tid}/task_lines/{id}",
        r"/api/v1/invoices/{eid}/task_line_groups/{tid}/task_lines/{id:\d+}",
        traverse="/task_lines/{id}",
    )
    config.add_route(
        "/api/v1/invoices/{eid}/discount_lines/{id}",
        r"/api/v1/invoices/{eid}/discount_lines/{id:\d+}",
        traverse="/discount_lines/{id}",
    )
    config.add_route(
        "/api/v1/invoices/{eid}/post_ttc_lines/{id}",
        r"/api/v1/invoices/{eid}/post_ttc_lines/{id:\d+}",
        traverse="/post_ttc_lines/{id}",
    )

    config.add_route(
        "/api/v1/invoices/{id}/statuslogentries",
        r"/api/v1/invoices/{id:\d+}/statuslogentries",
        traverse="/tasks/{id}",
    )

    config.add_route(
        "/api/v1/invoices/{eid}/statuslogentries/{id}",
        r"/api/v1/invoices/{eid:\d+}/statuslogentries/{id:\d+}",
        traverse="/statuslogentries/{id}",
    )


def add_cancelinvoice_routes(config):
    """
    Add routes specific to cancelinvoices edition

    :param obj config: Pyramid config object
    """
    for collection in ("task_line_groups", "file_requirements", "total"):
        route = os.path.join(API_CINV_ITEM_ROUTE, collection)
        config.add_route(route, route, traverse="/tasks/{id}")

    FILE_REQ_ITEM_ROUTE = os.path.join(
        API_CINV_COLLECTION_ROUTE, "{eid}", "file_requirements", "{id}"
    )
    config.add_route(
        FILE_REQ_ITEM_ROUTE,
        FILE_REQ_ITEM_ROUTE,
        traverse="/indicators/{id}",
    )

    config.add_route(
        "/api/v1/cancelinvoices/{eid}/task_line_groups/{id}",
        r"/api/v1/cancelinvoices/{eid}/task_line_groups/{id:\d+}",
        traverse="/task_line_groups/{id}",
    )
    config.add_route(
        "/api/v1/cancelinvoices/{eid}/task_line_groups/{id}/task_lines",
        r"/api/v1/cancelinvoices/{eid}/task_line_groups/{id:\d+}/task_lines",
        traverse="/task_line_groups/{id}",
    )
    config.add_route(
        "/api/v1/cancelinvoices/{eid}/task_line_groups/{tid}/task_lines/{id}",
        r"/api/v1/cancelinvoices/{eid}/task_line_groups/{tid}/task_lines/{id:\d+}",
        traverse="/task_lines/{id}",
    )

    config.add_route(
        "/api/v1/cancelinvoices/{id}/statuslogentries",
        r"/api/v1/cancelinvoices/{id:\d+}/statuslogentries",
        traverse="/tasks/{id}",
    )

    config.add_route(
        "/api/v1/cancelinvoices/{eid}/statuslogentries/{id}",
        r"/api/v1/cancelinvoices/{eid:\d+}/statuslogentries/{id:\d+}",
        traverse="/statuslogentries/{id}",
    )


def add_invoice_views(config):
    """
    Add Invoice related views to the current configuration
    """
    # Rest service for Estimation add
    config.add_rest_service(
        InvoiceAddRestView,
        collection_context=Company,
        collection_route_name=API_INVOICE_ADD_ROUTE,
        view_rights=PERMISSIONS["context.add_invoice"],
        add_rights=PERMISSIONS["context.add_invoice"],
    )
    # Form configuration view
    config.add_view(
        InvoiceAddRestView,
        route_name=API_INVOICE_ADD_ROUTE,
        attr="form_config",
        renderer="json",
        request_param="form_config",
        context=Company,
        permission=PERMISSIONS["company.view"],
    )
    # Invoice Edit view
    config.add_rest_service(
        InvoiceRestView,
        route_name="/api/v1/invoices/{id}",
        context=Invoice,
        view_rights=PERMISSIONS["company.view"],
        edit_rights=PERMISSIONS["context.edit_invoice"],
        delete_rights=PERMISSIONS["context.delete_invoice"],
    )

    # Form configuration view
    config.add_view(
        InvoiceRestView,
        attr="form_config",
        route_name="/api/v1/invoices/{id}",
        renderer="json",
        request_param="form_config",
        context=Invoice,
        permission=PERMISSIONS["company.view"],
    )

    # Status View
    config.add_view(
        InvoiceStatusRestView,
        route_name="/api/v1/invoices/{id}",
        request_param="action=status",
        request_method="POST",
        renderer="json",
        context=Invoice,
        permission=PERMISSIONS["context.edit_invoice"],
    )
    # Related estimation informations
    config.add_view(
        InvoiceRestView,
        route_name="/api/v1/invoices/{id}",
        attr="related_estimation",
        renderer="json",
        request_param="related_estimation",
        context=Invoice,
        permission=PERMISSIONS["context.edit_invoice"],
    )

    # Task linegroup views
    config.add_rest_service(
        TaskLineGroupRestView,
        "/api/v1/invoices/{eid}/task_line_groups/{id}",
        collection_route_name="/api/v1/invoices/{id}/task_line_groups",
        collection_context=Invoice,
        context=TaskLineGroup,
        view_rights=PERMISSIONS["company.view"],
        add_rights=PERMISSIONS["context.edit_invoice"],
        edit_rights=PERMISSIONS["context.edit_invoice"],
        delete_rights=PERMISSIONS["context.edit_invoice"],
    )
    config.add_view(
        TaskLineGroupRestView,
        route_name="/api/v1/invoices/{id}/task_line_groups",
        attr="post_load_groups_from_catalog_view",
        request_param="action=load_from_catalog",
        request_method="POST",
        renderer="json",
        context=Invoice,
        permission=PERMISSIONS["context.edit_invoice"],
    )
    # Task line views
    config.add_rest_service(
        TaskLineRestView,
        route_name="/api/v1/invoices/{eid}/task_line_groups/{tid}/task_lines/{id}",
        collection_route_name="/api/v1/invoices/{eid}/task_line_groups/{id}/task_lines",
        collection_context=TaskLineGroup,
        context=TaskLine,
        view_rights=PERMISSIONS["company.view"],
        add_rights=PERMISSIONS["context.edit_invoice"],
        edit_rights=PERMISSIONS["context.edit_invoice"],
        delete_rights=PERMISSIONS["context.edit_invoice"],
    )
    config.add_view(
        TaskLineRestView,
        route_name="/api/v1/invoices/{eid}/task_line_groups/{id}/task_lines",
        attr="post_load_from_catalog_view",
        request_param="action=load_from_catalog",
        request_method="POST",
        renderer="json",
        context=TaskLineGroup,
        permission=PERMISSIONS["context.edit_invoice"],
    )
    # Discount line views
    config.add_rest_service(
        DiscountLineRestView,
        "/api/v1/invoices/{eid}/discount_lines/{id}",
        collection_route_name="/api/v1/invoices/{id}/discount_lines",
        collection_context=Invoice,
        context=DiscountLine,
        view_rights=PERMISSIONS["company.view"],
        add_rights=PERMISSIONS["context.edit_invoice"],
        edit_rights=PERMISSIONS["context.edit_invoice"],
        delete_rights=PERMISSIONS["context.edit_invoice"],
    )
    config.add_view(
        DiscountLineRestView,
        route_name="/api/v1/invoices/{id}/discount_lines",
        attr="post_percent_discount_view",
        request_param="action=insert_percent",
        request_method="POST",
        renderer="json",
        context=Invoice,
        permission=PERMISSIONS["context.edit_invoice"],
    )
    config.add_rest_service(
        PostTTCLineRestView,
        "/api/v1/invoices/{eid}/post_ttc_lines/{id}",
        collection_route_name="/api/v1/invoices/{id}/post_ttc_lines",
        collection_context=Invoice,
        context=PostTTCLine,
        view_rights=PERMISSIONS["company.view"],
        add_rights=PERMISSIONS["context.edit_invoice"],
        edit_rights=PERMISSIONS["context.edit_invoice"],
        delete_rights=PERMISSIONS["context.edit_invoice"],
    )
    # File requirements views
    config.add_rest_service(
        TaskFileRequirementRestView,
        route_name="/api/v1/invoices/{eid}/file_requirements/{id}",
        collection_route_name="/api/v1/invoices/{id}/file_requirements",
        collection_context=Invoice,
        context=SaleFileRequirement,
        collection_view_rights=PERMISSIONS["company.view"],
        view_rights=PERMISSIONS["context.view_indicator"],
    )
    config.add_view(
        TaskFileRequirementRestView,
        route_name="/api/v1/invoices/{eid}/file_requirements/{id}",
        attr="validation_status",
        request_method="POST",
        request_param="action=validation_status",
        renderer="json",
        context=SaleFileRequirement,
        permission=PERMISSIONS["context.validate_indicator"],
    )
    config.add_view(
        task_total_view,
        route_name="/api/v1/invoices/{id}/total",
        request_method="GET",
        renderer="json",
        xhr=True,
        context=Invoice,
        permission=PERMISSIONS["company.view"],
    )

    config.add_rest_service(
        TaskStatusLogEntryRestView,
        "/api/v1/invoices/{eid}/statuslogentries/{id}",
        collection_route_name="/api/v1/invoices/{id}/statuslogentries",
        collection_context=Invoice,
        context=StatusLogEntry,
        collection_view_rights=PERMISSIONS["company.view"],
        add_rights=PERMISSIONS["company.view"],
        view_rights=PERMISSIONS["context.view_statuslogentry"],
        edit_rights=PERMISSIONS["context.edit_statuslogentry"],
        delete_rights=PERMISSIONS["context.delete_statuslogentry"],
    )

    config.add_view(
        TaskFileRestView,
        route_name=API_INVOICE_FILES_ROUTE,
        renderer="json",
        request_method="POST",
        attr="post",
        context=Invoice,
        permission=PERMISSIONS["context.add_file"],
    )


def add_cancelinvoice_views(config):
    """
    Add cancelinvoice related views to the current configuration

    :param obj config: The current Pyramid configuration
    """
    config.add_rest_service(
        CancelInvoiceRestView,
        route_name="/api/v1/cancelinvoices/{id}",
        context=CancelInvoice,
        view_rights=PERMISSIONS["company.view"],
        edit_rights=PERMISSIONS["context.edit_cancelinvoice"],
        delete_rights=PERMISSIONS["context.delete_cancelinvoice"],
    )

    # Form configuration view
    config.add_view(
        CancelInvoiceRestView,
        route_name="/api/v1/cancelinvoices/{id}",
        attr="form_config",
        renderer="json",
        request_param="form_config",
        context=CancelInvoice,
        permission=PERMISSIONS["company.view"],
    )

    # Status View
    config.add_view(
        CancelInvoiceStatusRestView,
        route_name="/api/v1/cancelinvoices/{id}",
        request_param="action=status",
        request_method="POST",
        renderer="json",
        context=CancelInvoice,
        permission=PERMISSIONS["context.edit_cancelinvoice"],
    )

    # Task linegroup views
    config.add_rest_service(
        TaskLineGroupRestView,
        route_name="/api/v1/cancelinvoices/{eid}/task_line_groups/{id}",
        collection_route_name="/api/v1/cancelinvoices/{id}/task_line_groups",
        collection_context=CancelInvoice,
        context=TaskLineGroup,
        view_rights=PERMISSIONS["company.view"],
        add_rights=PERMISSIONS["context.edit_cancelinvoice"],
        edit_rights=PERMISSIONS["context.edit_cancelinvoice"],
        delete_rights=PERMISSIONS["context.edit_cancelinvoice"],
    )
    config.add_view(
        TaskLineGroupRestView,
        route_name="/api/v1/cancelinvoices/{id}/task_line_groups",
        attr="post_load_groups_from_catalog_view",
        request_param="action=load_from_catalog",
        request_method="POST",
        renderer="json",
        context=CancelInvoice,
        permission=PERMISSIONS["context.edit_cancelinvoice"],
    )
    # Task line views
    config.add_rest_service(
        TaskLineRestView,
        route_name=(
            "/api/v1/cancelinvoices/{eid}/task_line_groups/{tid}/task_lines/{id}"
        ),
        collection_route_name=(
            "/api/v1/cancelinvoices/{eid}/task_line_groups/{id}/task_lines"
        ),
        context=TaskLine,
        collection_context=TaskLineGroup,
        view_rights=PERMISSIONS["company.view"],
        add_rights=PERMISSIONS["context.edit_cancelinvoice"],
        edit_rights=PERMISSIONS["context.edit_cancelinvoice"],
        delete_rights=PERMISSIONS["context.edit_cancelinvoice"],
    )
    config.add_view(
        TaskLineRestView,
        route_name="/api/v1/cancelinvoices/{eid}/task_line_groups/{id}/task_lines",
        attr="post_load_from_catalog_view",
        request_param="action=load_from_catalog",
        request_method="POST",
        renderer="json",
        context=TaskLineGroup,
        permission=PERMISSIONS["context.edit_cancelinvoice"],
    )
    # File requirements views
    config.add_rest_service(
        TaskFileRequirementRestView,
        route_name="/api/v1/cancelinvoices/{eid}/file_requirements/{id}",
        collection_route_name="/api/v1/cancelinvoices/{id}/file_requirements",
        context=SaleFileRequirement,
        collection_context=CancelInvoice,
        collection_view_rights=PERMISSIONS["company.view"],
        view_rights=PERMISSIONS["company.view"],
    )
    config.add_view(
        TaskFileRequirementRestView,
        route_name="/api/v1/cancelinvoices/{eid}/file_requirements/{id}",
        attr="validation_status",
        request_method="POST",
        request_param="action=validation_status",
        renderer="json",
        context=SaleFileRequirement,
        permission=PERMISSIONS["context.validate_indicator"],
    )
    config.add_view(
        task_total_view,
        route_name="/api/v1/cancelinvoices/{id}/total",
        request_method="GET",
        renderer="json",
        xhr=True,
        context=CancelInvoice,
        permission=PERMISSIONS["company.view"],
    )

    config.add_rest_service(
        TaskStatusLogEntryRestView,
        "/api/v1/cancelinvoices/{eid}/statuslogentries/{id}",
        collection_route_name="/api/v1/cancelinvoices/{id}/statuslogentries",
        collection_context=CancelInvoice,
        context=StatusLogEntry,
        collection_view_rights=PERMISSIONS["company.view"],
        add_rights=PERMISSIONS["company.view"],
        view_rights=PERMISSIONS["context.view_statuslogentry"],
        edit_rights=PERMISSIONS["context.edit_statuslogentry"],
        delete_rights=PERMISSIONS["context.delete_statuslogentry"],
    )

    config.add_view(
        TaskFileRestView,
        route_name=API_CINV_FILES_ROUTE,
        renderer="json",
        request_method="POST",
        attr="post",
        context=CancelInvoice,
        permission=PERMISSIONS["context.add_file"],
    )


def includeme(config):
    add_invoice_routes(config)
    add_cancelinvoice_routes(config)
    add_invoice_views(config)
    add_cancelinvoice_views(config)

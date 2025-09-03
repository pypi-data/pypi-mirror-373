import logging

from caerp.consts.permissions import PERMISSIONS
from caerp.models.task import Task
from caerp.models.project import Project
from caerp.views import TreeMixin
from caerp.views.company.routes import COMPANY_INVOICE_ADD_ROUTE
from caerp.views.invoices.lists import (
    CompanyInvoicesListView,
    CompanyInvoicesCsvView,
    CompanyInvoicesXlsView,
    CompanyInvoicesOdsView,
    filter_all_status,
)
from caerp.views.project.project import (
    ProjectListView,
)
from caerp.views.project.routes import (
    PROJECT_ITEM_INVOICE_ROUTE,
    PROJECT_ITEM_INVOICE_EXPORT_ROUTE,
)


logger = logging.getLogger(__name__)


class ProjectInvoiceListView(CompanyInvoicesListView, TreeMixin):
    """
    Invoice list for one given company
    """

    route_name = PROJECT_ITEM_INVOICE_ROUTE

    add_template_vars = CompanyInvoicesListView.add_template_vars + ("add_url",)

    @property
    def add_url(self):
        return self.request.route_path(
            COMPANY_INVOICE_ADD_ROUTE,
            id=self.context.company_id,
            _query={"project_id": self.context.id},
        )

    def _get_company_id(self, appstruct):
        return self.request.context.company_id

    @property
    def title(self):
        return "Factures du dossier {0}".format(self.request.context.name)

    def filter_project(self, query, appstruct):
        self.populate_navigation()
        query = query.filter(Task.project_id == self.context.id)
        return query


class ProjectInvoicesCsvView(CompanyInvoicesCsvView):
    def _get_company_id(self, appstruct):
        return self.request.context.company_id

    def filter_project(self, query, appstruct):
        logger.debug(" + Filtering by project_id")
        return query.filter(Task.project_id == self.context.id)

    filter_status = filter_all_status


class ProjectInvoicesXlsView(CompanyInvoicesXlsView):
    def _get_company_id(self, appstruct):
        return self.request.context.company_id

    def filter_project(self, query, appstruct):
        logger.debug(" + Filtering by project_id")
        return query.filter(Task.project_id == self.context.id)

    filter_status = filter_all_status


class ProjectInvoicesOdsView(CompanyInvoicesOdsView):
    def _get_company_id(self, appstruct):
        return self.request.context.company_id

    def filter_project(self, query, appstruct):
        logger.debug(" + Filtering by project_id")
        return query.filter(Task.project_id == self.context.id)

    filter_status = filter_all_status


def includeme(config):
    config.add_tree_view(
        ProjectInvoiceListView,
        parent=ProjectListView,
        renderer="project/invoices.mako",
        layout="project",
        context=Project,
        permission=PERMISSIONS["company.view"],
    )
    config.add_view(
        ProjectInvoicesCsvView,
        route_name=PROJECT_ITEM_INVOICE_EXPORT_ROUTE,
        match_param="extension=csv",
        context=Project,
        permission=PERMISSIONS["company.view"],
    )

    config.add_view(
        ProjectInvoicesOdsView,
        route_name=PROJECT_ITEM_INVOICE_EXPORT_ROUTE,
        match_param="extension=ods",
        context=Project,
        permission=PERMISSIONS["company.view"],
    )

    config.add_view(
        ProjectInvoicesXlsView,
        route_name=PROJECT_ITEM_INVOICE_EXPORT_ROUTE,
        match_param="extension=xls",
        context=Project,
        permission=PERMISSIONS["company.view"],
    )

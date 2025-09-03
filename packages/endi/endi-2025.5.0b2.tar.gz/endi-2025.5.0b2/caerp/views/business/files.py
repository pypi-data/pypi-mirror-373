from caerp.consts.permissions import PERMISSIONS
from caerp.models.project.business import Business
from caerp.views.business.routes import (
    BUSINESS_ITEM_FILE_ROUTE,
    BUSINESS_ITEM_ADD_FILE_ROUTE,
)
from caerp.views.project.project import ProjectEntryPointView
from caerp.views.project.files import (
    ProjectFileAddView,
    ProjectFilesView,
)

from .business import BusinessOverviewView


class BusinessFileAddView(ProjectFileAddView):
    route_name = BUSINESS_ITEM_ADD_FILE_ROUTE


class BusinessFilesView(ProjectFilesView):
    route_name = BUSINESS_ITEM_FILE_ROUTE

    @property
    def title(self):
        return "Fichiers attachés au dossier {0}".format(self.context.project.name)

    def get_project_id(self):
        return self.context.project_id

    def _get_js_app_options(self):
        result = super()._get_js_app_options()
        result["business_id"] = self.context.id
        return result


def includeme(config):
    config.add_tree_view(
        BusinessFileAddView,
        parent=BusinessOverviewView,
        permission=PERMISSIONS["context.add_file"],
        layout="default",
        renderer="caerp:templates/base/formpage.mako",
        context=Business,
    )
    config.add_tree_view(
        BusinessFilesView,
        parent=ProjectEntryPointView,
        permission=PERMISSIONS["company.view"],
        renderer="caerp:templates/business/files.mako",
        layout="business",
        context=Business,
    )

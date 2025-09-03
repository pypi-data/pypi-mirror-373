import logging
from caerp.consts.permissions import PERMISSIONS
from caerp.models.project.project import Project
from caerp.utils.menu import (
    MenuItem,
    Menu,
)
from caerp.default_layouts import DefaultLayout
from caerp.views.project.routes import (
    PROJECT_ITEM_ROUTE,
    PROJECT_ITEM_ESTIMATION_ROUTE,
    PROJECT_ITEM_INVOICE_ROUTE,
    PROJECT_ITEM_PHASE_ROUTE,
    PROJECT_ITEM_GENERAL_ROUTE,
    PROJECT_ITEM_BUSINESS_ROUTE,
    PROJECT_ITEM_FILE_ROUTE,
    PROJECT_ITEM_EXPENSES_ROUTE,
)


logger = logging.getLogger(__name__)


ProjectMenu = Menu(name="projectmenu")


def deferred_phase_show_perms(item, kw):
    """
    Check if the phase menu should be shown
    """
    request = kw["request"]
    return True and len(request.context.phases) > 1


ProjectMenu.add(
    MenuItem(
        name="project_businesses",
        label="Affaires",
        title="Liste des affaires",
        route_name=PROJECT_ITEM_BUSINESS_ROUTE,
        icon="list-alt",
        perm=PERMISSIONS["context.list_businesses"],
    )
)

ProjectMenu.add(
    MenuItem(
        name="project_estimations",
        label="Devis",
        title="Tous les devis",
        route_name=PROJECT_ITEM_ESTIMATION_ROUTE,
        icon="file-list",
        perm=PERMISSIONS["company.view"],
    )
)
ProjectMenu.add(
    MenuItem(
        name="project_invoices",
        label="Factures",
        title="Toutes les factures",
        route_name=PROJECT_ITEM_INVOICE_ROUTE,
        icon="file-invoice-euro",
        perm=PERMISSIONS["company.view"],
    )
)
ProjectMenu.add(
    MenuItem(
        name="project_phases",
        label="Sous-dossiers",
        title="Devis/Factures par sous-dossier",
        route_name=PROJECT_ITEM_PHASE_ROUTE,
        icon="folder-open",
        perm=PERMISSIONS["context.add_phase"],
    )
)
ProjectMenu.add(
    MenuItem(
        name="expenses",
        label="Achats liés",
        route_name=PROJECT_ITEM_EXPENSES_ROUTE,
        icon="box",
        perm=PERMISSIONS["company.view"],
    )
)
ProjectMenu.add(
    MenuItem(
        name="project_files",
        label="Fichiers",
        title="Fichiers",
        route_name=PROJECT_ITEM_FILE_ROUTE,
        icon="paperclip",
        perm=PERMISSIONS["company.view"],
    )
)
ProjectMenu.add(
    MenuItem(
        name="project_general",
        label="Informations",
        title="Informations générales",
        route_name=PROJECT_ITEM_GENERAL_ROUTE,
        icon="info-circle",
    )
)


class ProjectLayout(DefaultLayout):
    """
    Layout for project related pages

    Provide the main page structure for project view
    """

    def __init__(self, context, request):
        DefaultLayout.__init__(self, context, request)
        if isinstance(context, Project):
            self.current_project_object = context
        elif hasattr(context, "project"):
            self.current_project_object = context.project
        else:
            raise KeyError(
                "Can't retrieve the associated project object, \
                           current context : %s"
                % context
            )

    @property
    def edit_url(self):
        return self.request.route_path(
            PROJECT_ITEM_ROUTE,
            id=self.current_project_object.id,
            _query={"action": "edit"},
        )

    @property
    def details_url(self):
        return self.request.route_path(
            PROJECT_ITEM_GENERAL_ROUTE,
            id=self.current_project_object.id,
        )

    @property
    def customer_labels(self):
        return (customer.label for customer in self.current_project_object.customers)

    @property
    def projectmenu(self):
        ProjectMenu.set_current(self.current_project_object)
        ProjectMenu.bind(current_project=self.current_project_object)
        return ProjectMenu


def includeme(config):
    config.add_layout(
        ProjectLayout, template="caerp:templates/project/layout.mako", name="project"
    )

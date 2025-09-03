import logging

from caerp.consts.permissions import PERMISSIONS
from caerp.models.project.business import Business
from caerp.utils.menu import (
    MenuItem,
    Menu,
)
from caerp.utils.widgets import POSTButton
from caerp.default_layouts import DefaultLayout
from caerp.views.business.routes import (
    BUSINESS_ITEM_ROUTE,
    BUSINESS_ITEM_OVERVIEW_ROUTE,
    BUSINESS_ITEM_INVOICE_ROUTE,
    BUSINESS_ITEM_FILE_ROUTE,
    BUSINESS_ITEM_EXPENSES_ROUTE,
)
from caerp.views.training.routes import (
    BUSINESS_BPF_DATA_FORM_URL,
    BUSINESS_BPF_DATA_LIST_URL,
)


logger = logging.getLogger(__name__)


BusinessMenu = Menu(name="businessmenu")
BusinessMenu.add(
    MenuItem(
        name="overview",
        label="Vue générale",
        route_name=BUSINESS_ITEM_OVERVIEW_ROUTE,
        icon="info-circle",
        perm=PERMISSIONS["company.view"],
    )
)
BusinessMenu.add(
    MenuItem(
        name="business_invoices",
        label="Factures",
        route_name=BUSINESS_ITEM_INVOICE_ROUTE,
        icon="file-invoice-euro",
        perm=PERMISSIONS["company.view"],
    )
)
BusinessMenu.add(
    MenuItem(
        name="business_files",
        label="Fichiers",
        route_name=BUSINESS_ITEM_FILE_ROUTE,
        icon="paperclip",
        perm=PERMISSIONS["company.view"],
    )
)
BusinessMenu.add(
    MenuItem(
        name="expenses",
        label="Achats liés",
        route_name=BUSINESS_ITEM_EXPENSES_ROUTE,
        icon="box",
        perm=PERMISSIONS["company.view"],
    )
)
BusinessMenu.add(
    MenuItem(
        name="bpf_data",
        label="Données BPF",
        route_name=BUSINESS_BPF_DATA_LIST_URL,
        other_route_name=BUSINESS_BPF_DATA_FORM_URL,
        perm=PERMISSIONS["context.edit_bpf"],
        icon="chart-pie",
    )
)


class BusinessLayout(DefaultLayout):
    """
    Layout for business related pages

    Provide the main page structure for project view
    """

    def __init__(self, context, request):
        DefaultLayout.__init__(self, context, request)

        if isinstance(context, Business):
            self.current_business_object = context
        elif hasattr(context, "business"):
            self.current_business_object = context.business
        else:
            raise Exception(
                "Can't retrieve the current business used in the "
                "business layout, context is : %s" % context
            )

    @property
    def edit_url(self):
        return self.request.route_path(
            BUSINESS_ITEM_ROUTE,
            id=self.current_business_object.id,
            _query={"action": "edit"},
        )

    @property
    def businessmenu(self):
        BusinessMenu.set_current(self.current_business_object)
        return BusinessMenu


def includeme(config):
    config.add_layout(
        BusinessLayout,
        template="caerp:templates/business/layout.mako",
        name="business",
    )

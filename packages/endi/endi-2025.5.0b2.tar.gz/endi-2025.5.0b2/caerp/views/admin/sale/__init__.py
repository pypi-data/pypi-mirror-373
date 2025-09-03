import os

from caerp.consts.permissions import PERMISSIONS
from caerp.views.admin import (
    AdminIndexView,
    BASE_URL,
)
from caerp.views.admin.tools import BaseAdminIndexView


SALE_URL = os.path.join(BASE_URL, "sales")


class SaleIndexView(BaseAdminIndexView):
    route_name = SALE_URL
    title = "Module Ventes"
    description = (
        "Configurer les mentions des devis et factures, les unités de prestation…"
    )
    permission = PERMISSIONS["global.config_sale"]


def includeme(config):
    config.add_route(SALE_URL, SALE_URL)
    config.add_admin_view(SaleIndexView, parent=AdminIndexView)
    config.include(".forms")
    config.include(".pdf")
    config.include(".business_cycle")
    config.include(".accounting")
    config.include(".catalog")

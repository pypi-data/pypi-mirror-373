import os

from caerp.consts.permissions import PERMISSIONS
from caerp.views.admin import (
    AdminIndexView,
    BASE_URL,
)
from caerp.views.admin.tools import BaseAdminIndexView


SUPPLIER_URL = os.path.join(BASE_URL, "suppliers")


class SupplierIndexView(BaseAdminIndexView):
    route_name = SUPPLIER_URL
    title = "Module Fournisseurs"
    description = (
        "Configurer les comptes, les exports comptables et la numérotation des "
        "factures fournisseur."
    )
    permission = PERMISSIONS["global.config_supply"]


def includeme(config):
    config.add_route(SUPPLIER_URL, SUPPLIER_URL)
    config.add_admin_view(
        SupplierIndexView,
        parent=AdminIndexView,
    )
    config.include(".accounting")
    config.include(".numbers")
    config.include(".internalnumbers")

import os
from caerp.consts.permissions import PERMISSIONS
from caerp.views.admin.sale import (
    SALE_URL,
    SaleIndexView,
)
from caerp.views.admin.tools import BaseAdminIndexView


ACCOUNTING_INDEX_URL = os.path.join(SALE_URL, "accounting")


class SaleAccountingIndex(BaseAdminIndexView):
    title = "Configuration comptable du module de vente"
    description = "Configurer la génération des écritures de vente et d'encaissement"
    route_name = ACCOUNTING_INDEX_URL
    permission = PERMISSIONS["global.config_accounting"]


def includeme(config):
    config.add_route(ACCOUNTING_INDEX_URL, ACCOUNTING_INDEX_URL)
    config.add_admin_view(
        SaleAccountingIndex,
        parent=SaleIndexView,
    )
    config.include(".common")
    config.include(".invoice")
    config.include(".internalinvoice")
    config.include(".numbers")

    # Est importé depuis views/internal_invoicing/
    # (ce qui permet de l'exclure en mode solo)
    # config.include(".internal_invoicing_numbers")
    config.include(".receipts")

    config.include(".tva")

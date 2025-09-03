import os

from caerp.consts.permissions import PERMISSIONS
from caerp.views.admin.sale import SaleIndexView, SALE_URL
from caerp.views.admin.tools import BaseAdminIndexView


PDF_URL = os.path.join(SALE_URL, "pdf")


class PdfIndexView(BaseAdminIndexView):
    title = "Sorties PDF"
    description = "Configurer les mentions générales des sorties pdf"
    route_name = PDF_URL
    permission = PERMISSIONS["global.config_sale"]


def includeme(config):
    config.add_route(PDF_URL, PDF_URL)
    config.add_admin_view(
        PdfIndexView,
        parent=SaleIndexView,
    )
    config.include(".common")
    config.include(".estimation")
    config.include(".invoice")

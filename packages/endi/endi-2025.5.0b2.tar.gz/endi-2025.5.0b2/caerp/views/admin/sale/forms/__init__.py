import os

from caerp.consts.permissions import PERMISSIONS
from caerp.views.admin.sale import (
    SaleIndexView,
    SALE_URL as BASE_URL,
)
from caerp.views.admin.tools import BaseAdminIndexView


FORMS_URL = os.path.join(BASE_URL, "forms")


class FormsIndexView(BaseAdminIndexView):
    route_name = FORMS_URL
    title = "Formulaire de saisie des Devis/Facture"
    description = (
        "Configurer les options proposées dans les formulaires de saisie des"
        " devis/factures"
    )

    permission = PERMISSIONS["global.config_sale"]


def includeme(config):
    config.add_route(FORMS_URL, FORMS_URL)
    config.add_admin_view(FormsIndexView, parent=SaleIndexView)
    config.include(".main")
    config.include(".fields")
    config.include(".insurance")
    config.include(".mentions")

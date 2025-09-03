import os

from caerp.views.admin import (
    AdminIndexView,
    BASE_URL,
)
from caerp.views.admin.tools import BaseAdminIndexView

SAP_URL = os.path.join(BASE_URL, "sap")


class SAPIndexView(BaseAdminIndexView):
    route_name = SAP_URL
    title = "Module SAP"
    description = "Configurer les options propres au service à la personne"


def includeme(config):
    config.add_route(SAP_URL, SAP_URL)
    config.add_admin_view(SAPIndexView, parent=AdminIndexView)
    config.include(".attestation")

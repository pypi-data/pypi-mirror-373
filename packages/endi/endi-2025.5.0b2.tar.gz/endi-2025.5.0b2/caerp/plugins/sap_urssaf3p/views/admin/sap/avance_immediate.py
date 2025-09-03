import os
from pyramid.httpexceptions import HTTPFound

from caerp.models.config import Config
from caerp.views.admin.tools import BaseAdminFormView
from caerp.plugins.sap.views.admin.sap import (
    SAPIndexView,
    SAP_URL,
)
from caerp.plugins.sap_urssaf3p.forms.admin.sap import SapAvanceImmediateConfigSchema


SAP_AVANCE_IMMEDIATE_URL = os.path.join(SAP_URL, "avance_immediate")


HELP_MSG = f"""
Configurez le compte bancaire sur lequel les encaissements automatiques
liés à l'avance immédiate de l'URSSAF seront affectés
"""


class SAPAvanceImmediateView(BaseAdminFormView):
    title = "Avance immédiate"
    description = "Configurer l'avance immédiate de l'URSSAF"
    route_name = SAP_AVANCE_IMMEDIATE_URL
    help_msg = HELP_MSG
    validation_msg = "L'avance immédiate SAP a bien été configurée"
    add_template_vars = ("help_msg",)
    keys = [
        "urssaf3p_payment_bank_id",
        "urssaf3p_automatic_payment_creation",
    ]
    schema = SapAvanceImmediateConfigSchema()

    def before(self, form):
        appstruct = {key: self.request.config.get(key) for key in self.keys}
        form.set_appstruct(appstruct)

    def submit_success(self, appstruct):
        for key in self.keys:
            Config.set(key, appstruct.get(key))
        self.dbsession.flush()
        self.request.session.flash(self.validation_msg)
        return HTTPFound(self.request.route_path(self.parent_view.route_name))


def includeme(config):
    config.add_route(SAP_AVANCE_IMMEDIATE_URL, SAP_AVANCE_IMMEDIATE_URL)
    config.add_admin_view(SAPAvanceImmediateView, parent=SAPIndexView)

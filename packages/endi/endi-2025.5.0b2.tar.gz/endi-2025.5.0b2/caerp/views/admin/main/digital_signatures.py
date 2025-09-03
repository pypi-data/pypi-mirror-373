import logging
import os

from pyramid.httpexceptions import HTTPFound

from caerp.consts.permissions import PERMISSIONS
from caerp.views.admin.tools import BaseAdminFormView
from caerp.forms import public_file_appstruct
from caerp.forms.admin.main.digital_signatures import DigitalSignaturesSchema
from caerp.models.config import ConfigFiles
from caerp.views.admin.main import (
    MAIN_ROUTE,
    MainIndexView,
)

DIGITAL_SIGNATURES_ROUTE = os.path.join(MAIN_ROUTE, "digital_signatures")

logger = logging.getLogger(__name__)


class AdminDigitalSignaturesView(BaseAdminFormView):
    """
    Digital signatures welcome page
    """

    title = "Signatures numérisées"
    description = "Configurer les signatures manuscrites numérisées"
    route_name = DIGITAL_SIGNATURES_ROUTE
    schema = DigitalSignaturesSchema()
    validation_msg = "Informations mises à jour avec succès"
    permission = PERMISSIONS["global.config_cae"]

    def before(self, form):
        """
        Add the appstruct to the form
        :param form:
        """
        cae_manager_digital_signature = ConfigFiles.get(
            "cae_manager_digital_signature.png"
        )
        appstruct = {}
        if cae_manager_digital_signature is not None:
            appstruct["cae_manager_digital_signature"] = public_file_appstruct(
                self.request,
                "cae_manager_digital_signature.png",
                cae_manager_digital_signature,
            )
        form.set_appstruct(appstruct)

    def submit_success(self, appstruct):
        """
        insert digital signature image in database
        :param appstruct:
        :return:
        """
        cae_manager_digital_signature = appstruct.pop(
            "cae_manager_digital_signature", None
        )

        if cae_manager_digital_signature:
            digital_signature = ConfigFiles()
            if cae_manager_digital_signature.get("delete"):
                digital_signature.delete("cae_manager_digital_signature.png")
            else:
                cae_manager_digital_signature["_acl"] = [
                    ("Allow", "group:admin", "view"),
                ]
                digital_signature.set(
                    "cae_manager_digital_signature.png", cae_manager_digital_signature
                )
            self.request.session.pop("substanced.tempstore")
            self.request.session.changed()

        self.request.session.flash(self.validation_msg)
        back_link = self.back_link
        result = None
        if back_link is not None:
            result = HTTPFound(back_link)
        return result


def includeme(config):
    config.add_route(DIGITAL_SIGNATURES_ROUTE, DIGITAL_SIGNATURES_ROUTE)
    config.add_admin_view(
        AdminDigitalSignaturesView,
        parent=MainIndexView,
    )

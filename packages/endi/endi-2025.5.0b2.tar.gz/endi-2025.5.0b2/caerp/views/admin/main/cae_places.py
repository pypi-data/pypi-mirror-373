import logging
import os
import json

from pyramid.httpexceptions import HTTPFound
from deform import Button

from caerp.consts.permissions import PERMISSIONS
from caerp.utils.strings import pluralize
from caerp.views.admin.tools import BaseAdminFormView
from caerp.forms import public_file_appstruct

from caerp.forms.admin.main.cae_places import CAEPlacesSchema
from caerp.models.config import ConfigFiles
from caerp.views.admin.main import (
    MAIN_ROUTE,
    MainIndexView,
)

CONFIG_CAE_LOCATIONS = os.path.join(MAIN_ROUTE, "config_cae_places")

logger = logging.getLogger(__name__)


submit_btn = Button(
    name="submit",
    type="submit",
    title="Remplacer la liste",
    icon="redo-alt",
    css_class="btn btn-primary",
)


class CAEPlacesView(BaseAdminFormView):
    """
    Page des lieux ressources pour la carte de l'annuaire des enseignes
    """

    title = "Lieux ressources"
    description = (
        "Configuration des lieux ressources qui apparaissent sur la "
        "cartographie de l'annuaire des enseignes"
    )
    message = "Aucun fichier de lieux ressources trouvé"
    validation_msg = (
        "Le nouveau fichier le lieux ressources a été pris en compte avec succès"
    )
    route_name = CONFIG_CAE_LOCATIONS
    schema = CAEPlacesSchema()
    buttons = (submit_btn,)
    add_template_vars = (
        "message",
        "geojson",
    )

    permission = PERMISSIONS["global.config_cae"]
    geojson = None

    def parse_geojson(self, geojson):
        """
        parsing et vérification du fichier geojson
        """
        if geojson is None:
            message = "Aucun fichier de lieu trouvé"
            return
        data = geojson.getvalue()
        try:
            data = json.loads(data)
            self.geojson = data

            self.message = (
                "La liste contient {nb_locations}, lieu{_x} ressource{_s}".format(
                    nb_locations=len(data["features"]),
                    _x=pluralize(data["features"], "x"),
                    _s=pluralize(data["features"], "s"),
                )
            )
        except Exception as e:
            self.message = "Le fichier téléversé ne semble pas correct"

    def before(self, form):
        """
        Add the appstruct to the form
        :param form:
        """
        locations = ConfigFiles.get("cae_places.geojson")
        self.parse_geojson(locations)
        appstruct = {}
        if locations is not None:
            appstruct["cae_places"] = public_file_appstruct(
                self.request,
                "cae_places.geojson",
                locations,
            )
        form.set_appstruct(appstruct)

    def submit_success(self, appstruct):
        """
        insert digital signature image in database
        :param appstruct:
        :return:
        """
        locations = appstruct.pop("cae_places", None)

        if locations:
            if locations.get("delete"):
                ConfigFiles.delete("cae_places.geojson")
            else:
                # Force mimetype ; caues Windows OS does not know geoJSON and will push it as application/octet-stream
                # Which makes JS part fail at render time
                locations["mimetype"] = "application/geo+json"
                ConfigFiles.set("cae_places.geojson", locations)
            self.request.session.pop("substanced.tempstore")
            self.request.session.changed()
        locations = ConfigFiles.get("cae_places.geojson")
        if locations:
            self.parse_geojson(locations)
            self.validation_msg = self.validation_msg + " : " + self.message

        self.request.session.flash(self.validation_msg)
        back_link = self.back_link
        result = None
        if back_link is not None:
            result = HTTPFound(back_link)
        return result


def includeme(config):
    config.add_route(CONFIG_CAE_LOCATIONS, CONFIG_CAE_LOCATIONS)
    config.add_admin_view(
        CAEPlacesView,
        parent=MainIndexView,
        renderer="admin/places.mako",
    )

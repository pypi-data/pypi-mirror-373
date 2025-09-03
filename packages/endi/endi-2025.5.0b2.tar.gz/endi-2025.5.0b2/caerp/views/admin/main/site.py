import logging
import os

from caerp.consts.permissions import PERMISSIONS
from pyramid.httpexceptions import HTTPFound
from caerp.models.config import (
    Config,
    ConfigFiles,
)
from caerp.forms import (
    public_file_appstruct,
    flatten_appstruct_to_key_value,
)
from caerp.forms.admin.main.site import SiteConfigSchema
from caerp.views.admin.tools import (
    BaseAdminFormView,
)
from caerp.views.admin.main import (
    MainIndexView,
    MAIN_ROUTE,
)

MAIN_SITE_ROUTE = os.path.join(MAIN_ROUTE, "site")


logger = logging.getLogger(__name__)


class AdminSiteView(BaseAdminFormView):
    """
    Admin welcome page
    """

    title = "Pages de connexion et d’accueil"
    description = (
        "Configurer la page de connexion (photos et logo) et le message d’accueil"
    )
    route_name = MAIN_SITE_ROUTE
    schema = SiteConfigSchema()
    validation_msg = "Vos modification ont été enregistrées"
    permission = PERMISSIONS["global.config_cae"]

    def before(self, form):
        """
        Add the appstruct to the form
        """
        config_dict = self.request.config
        logo = ConfigFiles.get("logo.png")
        appstruct = {}
        if logo is not None:
            appstruct["logo"] = public_file_appstruct(self.request, "logo.png", logo)
        appstruct["welcome"] = config_dict.get("welcome", "")

        login_backgrounds = []
        for idx in range(10):
            photo_key = f"login_backgrounds.{idx}.photo"
            background_photo = ConfigFiles.get(photo_key)
            if background_photo is None:
                break
            background = {
                "index": idx,
                "photo": public_file_appstruct(
                    self.request, photo_key, background_photo
                ),
            }
            for key in ["title", "subtitle", "author"]:
                background[key] = config_dict.get(f"login_backgrounds.{idx}.{key}", "")
            login_backgrounds.append(background)
        appstruct["login_backgrounds"] = login_backgrounds

        form.set_appstruct(appstruct)

    def submit_success(self, appstruct):
        """
        Insert config informations into database
        """
        # la table config étant un stockage clé valeur
        # le merge_session_with_post ne peut être utilisé
        logo = appstruct.pop("logo", None)
        if logo:
            if logo.get("delete"):
                ConfigFiles.delete("logo.png")
            else:
                ConfigFiles.set("logo.png", logo)
            self.request.session.pop("substanced.tempstore")
            self.request.session.changed()

        backgrounds = appstruct["login_backgrounds"]
        backgrounds_images = [
            background.pop("photo", None) for background in backgrounds
        ]

        for idx, photo in enumerate(backgrounds_images):
            if photo is None:
                oldidx = backgrounds[idx]["index"]
                if idx != oldidx:
                    logger.debug(f"renaming photo {oldidx} into {idx}")
                    ConfigFiles.rename(
                        f"login_backgrounds.{oldidx}.photo",
                        f"login_backgrounds.{idx}.photo",
                    )
                continue
            ConfigFiles.set(f"login_backgrounds.{idx}.photo", photo)
            self.request.session.pop("substanced.tempstore")
            self.request.session.changed()
        ConfigFiles.delete(f"login_backgrounds.{len(backgrounds_images)}.photo")

        for key, value in flatten_appstruct_to_key_value(appstruct).items():
            Config.set(key, value)

        self.request.session.flash(self.validation_msg)
        back_link = self.back_link
        result = None
        if back_link is not None:
            result = HTTPFound(back_link)
        return result


#
# class AdminMainView(BaseAdminFormView):
#     """
#         Main configuration view
#     """
#     title = "Configuration générale"
#     route_name = MAIN_ROUTE
#     description = "Message d’accueil, logos, en-tête et pieds de page des \
# devis, factures / avoir)"
#
#     validation_msg = "La configuration a bien été modifiée"
#     schema = MainConfig()
#     buttons = (submit_btn,)
#
#     def before(self, form):
#         """
#             Add the appstruct to the form
#         """
#         config_dict = self.request.config
#         logo = ConfigFiles.get('logo.png')
#         appstruct = get_config_appstruct(self.request, config_dict, logo)
#         form.set_appstruct(appstruct)
#
#     def submit_success(self, appstruct):
#         """
#             Insert config informations into database
#         """
#         # la table config étant un stockage clé valeur
#         # le merge_session_with_post ne peut être utilisé
#         logo = appstruct['site'].pop('logo', None)
#         if logo:
#             ConfigFiles.set('logo.png', logo)
#             self.request.session.pop('substanced.tempstore')
#             self.request.session.changed()
#
#         dbdatas = self.dbsession.query(Config).all()
#         appstruct = get_config_dbdatas(appstruct)
#         dbdatas = merge_config_datas(dbdatas, appstruct)
#         for dbdata in dbdatas:
#             self.dbsession.merge(dbdata)
#         self.dbsession.flush()
#         self.request.session.flash(self.validation_msg)
#         return HTTPFound(self.request.route_path(self.route_name))


def includeme(config):
    config.add_route(MAIN_SITE_ROUTE, MAIN_SITE_ROUTE)
    config.add_admin_view(
        AdminSiteView,
        parent=MainIndexView,
    )

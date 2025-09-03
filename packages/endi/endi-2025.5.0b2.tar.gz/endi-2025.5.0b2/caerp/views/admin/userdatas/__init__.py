import os

from caerp.consts.permissions import PERMISSIONS
from caerp.views.admin import (
    AdminIndexView,
    BASE_URL,
)
from caerp.views.admin.tools import BaseAdminIndexView


USERDATAS_URL = os.path.join(BASE_URL, "userdatas")


class UserDatasIndexView(BaseAdminIndexView):
    route_name = USERDATAS_URL
    title = "Module Gestion sociale"
    description = "Module de gestion des données sociales : Configurer les \
typologies des données, les modèles de documents"
    permission = PERMISSIONS["global.config_userdatas"]


def includeme(config):
    config.add_route(USERDATAS_URL, USERDATAS_URL)
    config.add_admin_view(
        UserDatasIndexView,
        parent=AdminIndexView,
    )
    config.include(".options")
    config.include(".templates")
    config.include(".career_stage")
    config.include(".custom_fields")

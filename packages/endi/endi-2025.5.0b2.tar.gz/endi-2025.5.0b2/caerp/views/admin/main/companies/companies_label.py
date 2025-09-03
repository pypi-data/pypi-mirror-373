import os


from caerp.consts.permissions import PERMISSIONS
from caerp.views.admin.tools import BaseConfigView
from caerp.forms.admin import get_config_schema
from caerp.views.admin.main.companies import (
    MainCompaniesIndex,
    COMPANIES_INDEX_URL,
)

COMPANIES_LABEL_ROUTE = os.path.join(COMPANIES_INDEX_URL, "companies_label")


class CompaniesLabelView(BaseConfigView):
    title = "Désignation des enseignes"
    description = "Afficher le nom de l'entrepreneur à la suite du nom de l'enseigne"
    route_name = COMPANIES_LABEL_ROUTE

    keys = ("companies_label_add_user_name",)
    schema = get_config_schema(keys)


def includeme(config):
    config.add_route(COMPANIES_LABEL_ROUTE, COMPANIES_LABEL_ROUTE),
    config.add_admin_view(
        CompaniesLabelView,
        parent=MainCompaniesIndex,
        permission=PERMISSIONS["global.config_company"],
    )

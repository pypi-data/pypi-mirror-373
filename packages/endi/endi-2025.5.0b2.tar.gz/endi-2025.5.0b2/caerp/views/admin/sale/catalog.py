"""
Configuration générale du module vente:

    Mise en forme des PDFs
    Unité de prestation
"""
import logging
import os

from caerp.consts.permissions import PERMISSIONS
from caerp.forms.admin import get_config_schema

from caerp.views.admin.tools import (
    BaseConfigView,
)
from . import SALE_URL, SaleIndexView


logger = logging.getLogger(__name__)


FORM_CONFIG_URL = os.path.join(SALE_URL, "config")


class SaleCatalogAdminView(BaseConfigView):
    title = "Catalogue produit et Étude de prix"
    description = "Champs du catalogue, contributions à utiliser dans les études"
    route_name = FORM_CONFIG_URL
    validation_msg = "Les informations ont bien été enregistrées"

    keys = (
        "sale_catalog_notva_mode",
        "sale_catalog_sale_product_vae_taskline_template",
        "sale_catalog_sale_product_training_taskline_template",
        "price_study_uses_contribution",
        "price_study_uses_insurance",
    )
    schema = get_config_schema(keys)
    permission = PERMISSIONS["global.config_sale"]


def includeme(config):
    view = SaleCatalogAdminView
    config.add_route(view.route_name, view.route_name)
    config.add_admin_view(view, parent=SaleIndexView)

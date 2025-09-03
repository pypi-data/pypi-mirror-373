import os

import logging

from caerp.consts.permissions import PERMISSIONS
from caerp.forms.admin import get_config_schema
from caerp.views.admin.tools import (
    BaseConfigView,
    BaseAdminIndexView,
)
from caerp.views.admin.sale.accounting import (
    ACCOUNTING_INDEX_URL,
    SaleAccountingIndex,
)
from .invoice import (
    ModuleEditView,
    ModuleListView,
    ModuleAddView,
    ModuleDeleteView,
    ModuleDisableView,
)


logger = logging.getLogger(__name__)
INDEX_URL = os.path.join(ACCOUNTING_INDEX_URL, "internalinvoice")
CONFIG_URL = os.path.join(INDEX_URL, "config")

MODULE_COLLECTION_URL = os.path.join(INDEX_URL, "modules")
MODULE_ITEM_URL = os.path.join(MODULE_COLLECTION_URL, "{id}")


class IndexView(BaseAdminIndexView):
    title = "Factures internes"
    description = "Configurer les écritures des factures internes"
    route_name = INDEX_URL
    permission = PERMISSIONS["global.config_accounting"]


class ConfigView(BaseConfigView):
    """
    Cae information configuration
    """

    title = "Informations générales et modules prédéfinis"
    description = "Configuration du code journal pour les factures internes"
    route_name = CONFIG_URL

    validation_msg = "Les informations ont bien été enregistrées"
    keys = (
        "internalcode_journal",
        "internalcode_journal_encaissement",
        "internalnumero_analytique",
        "internalcompte_frais_annexes",
        "internalcompte_cg_banque",
        "internalbookentry_facturation_label_template",
        "internalcae_general_customer_account",
        "internalcae_third_party_customer_account",
        "internalcompte_rrr",
    )
    schema = get_config_schema(keys)
    info_message = """Configurez les exports comptables de votre CAE.</br >
<h4>Champs indispensables aux exports</h4>\
    <ul>\
        <li>Code journal</li>\
        <li>Numéro analytique de la CAE</li>\
        <li>Compte banque de l'entrepreneur</li>\
    </ul>
<h4>Champs relatifs aux frais et remises</h4>\
    <ul>\
      <li>Compte de frais annexes</li>\
      <li>Compte RRR (Rabais, Remises et Ristournes)</li>\
    </ul>
<h4>Configurez et activez des modules de retenues optionnels</h4>\
        <ul>\
    <li>Module RG Externe (spécifique bâtiment)</li>\
    <li>Module RG Interne (spécifique bâtiment)</li>\
    </ul>
<h4>Variables utilisables dans les gabarits de libellés</h4>\
    <p>Il est possible de personaliser les libellés comptables à l'aide d'un\
    gabarit. Plusieurs variables sont disponibles :</p>\
    <ul>\
      <li><code>{invoice.customer.label}</code> : nom du client facturé</li>\
      <li><code>{invoice.customer.code}</code> : code du client facturé</li>\
      <li><code>{company.code_compta}</code> : code analytique \
      de l'enseigne établissant la facture</li>\
      <li><code>{invoice.official_number}</code> : numéro de facture \
      (pour tronquer à 9 caractères : \
      <code>{invoice.official_number:.9}</code>)</li>\
      <li><code>{company.name}</code> : nom de l'enseigne établissant \
      la facture</li>\
    </ul>\
    <p>NB : Penser à séparer les variables, par exemple par des espaces, \
    sous peine de libellés peu lisibles.</p>\
    """
    permission = PERMISSIONS["global.config_accounting"]


class InternalModuleListView(ModuleListView):
    description = "Configuration des modules de contribution de la facturation interne"
    route_name = MODULE_COLLECTION_URL
    item_route_name = MODULE_ITEM_URL
    doctype = "internalinvoice"
    permission = PERMISSIONS["global.config_accounting"]


class InternalModuleAddView(ModuleAddView):
    doctype = "internalinvoice"
    route_name = MODULE_ITEM_URL
    permission = PERMISSIONS["global.config_accounting"]


class InternalModuleEditView(ModuleEditView):
    route_name = MODULE_ITEM_URL
    permission = PERMISSIONS["global.config_accounting"]


class InternalModuleDisableView(ModuleDisableView):
    route_name = MODULE_ITEM_URL
    permission = PERMISSIONS["global.config_accounting"]


class InternalModuleDeleteView(ModuleDeleteView):
    route_name = MODULE_ITEM_URL
    permission = PERMISSIONS["global.config_accounting"]


def add_routes(config):
    config.add_route(INDEX_URL, INDEX_URL)
    config.add_route(CONFIG_URL, CONFIG_URL)
    config.add_route(MODULE_COLLECTION_URL, MODULE_COLLECTION_URL)
    config.add_route(
        MODULE_ITEM_URL,
        MODULE_ITEM_URL,
        traverse="/custom_invoice_book_entry_modules/{id}",
    )


def includeme(config):
    add_routes(config)
    config.add_admin_view(
        IndexView,
        parent=SaleAccountingIndex,
    )
    config.add_admin_view(
        ConfigView,
        parent=IndexView,
    )
    config.add_admin_view(
        InternalModuleListView,
        parent=IndexView,
        renderer="admin/crud_list.mako",
    )
    config.add_admin_view(
        InternalModuleAddView,
        parent=InternalModuleListView,
        renderer="admin/crud_add_edit.mako",
        request_param="action=add",
    )
    config.add_admin_view(
        InternalModuleEditView,
        parent=InternalModuleListView,
        renderer="admin/crud_add_edit.mako",
    )
    config.add_admin_view(
        InternalModuleDisableView,
        parent=InternalModuleListView,
        request_param="action=disable",
        request_method="POST",
        require_csrf=True,
    )
    config.add_admin_view(
        InternalModuleDeleteView,
        parent=InternalModuleListView,
        request_param="action=delete",
        request_method="POST",
        require_csrf=True,
    )

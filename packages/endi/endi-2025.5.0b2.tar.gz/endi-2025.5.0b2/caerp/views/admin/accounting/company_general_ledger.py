import os
import logging

from sqlalchemy import asc

from caerp.consts.permissions import PERMISSIONS
from caerp.views.admin.accounting import (
    AccountingIndexView,
    ACCOUNTING_URL,
)
from caerp.models.accounting.general_ledger_account_wordings import (
    GeneralLedgerAccountWording,
)
from caerp.forms.accounting import (
    get_admin_general_ledger_account_wording_schema,
)

from caerp.views.admin.tools import (
    AdminCrudListView,
    BaseConfigView,
    BaseAdminIndexView,
    BaseAdminDeleteView,
    BaseAdminAddView,
    BaseAdminEditView,
)
from caerp.forms.admin import get_config_schema

from caerp.utils.widgets import Link, POSTButton

logger = logging.getLogger(__name__)

BASE_URL = os.path.join(ACCOUNTING_URL, "company_general_ledger")
GENERAL_LEDGER_ACCOUNT_SETTING_URL = os.path.join(
    BASE_URL, "general_ledger_account_setting"
)
GENERAL_LEDGER_ACCOUNT_WORDING_LIST_URL = os.path.join(
    BASE_URL, "general_ledger_account_wording_list"
)
GENERAL_LEDGER_ACCOUNT_WORDING_LIST_ITEM_URL = os.path.join(
    GENERAL_LEDGER_ACCOUNT_WORDING_LIST_URL, "{id}"
)


class GeneralLedgerIndexView(BaseAdminIndexView):
    title = "Grand Livre"
    description = (
        "Paramétrer l'état de gestion « Grand livre » visible par les entrepreneurs."
    )
    route_name = BASE_URL
    permission = PERMISSIONS["global.config_accounting_measure"]


class GeneralLedgerAccountSettingView(BaseConfigView):
    title = "Comptes à afficher"
    description = "Permet de sélectionner les comptes qui seront affichés aux\
    entrepreneurs"
    route_name = GENERAL_LEDGER_ACCOUNT_SETTING_URL
    redirect_route_name = BASE_URL

    validation_msg = "Les informations ont bien été enregistrées"
    keys = ("company_general_ledger_accounts_filter",)
    schema = get_config_schema(keys)
    permission = PERMISSIONS["global.config_accounting_measure"]

    @property
    def info_message(self):
        return """Toutes les écritures dont le compte commence par le préfixe fourni seront
        utilisées pour filter la liste des remontées comptables du grands livre. NB :
        Une liste de préfixe peut être fournie en les séparant par des virgules
        (ex : 42,43), un préfixe peut être exclu en plaçant le signe '-' devant (ex: 42,
        -425 incluera tous les comptes 42… sauf les comptes 425…)"""


class GeneralLedgerAccountWordingListView(AdminCrudListView):
    title = "Nom des numéros de comptes"
    description = "Permet d'afficher un nom correspondant au numéro de\
    compte dans le Grand Livre"
    columns = [
        "Numéro de compte",
        "Nom du compte",
    ]
    factory = GeneralLedgerAccountWording
    route_name = GENERAL_LEDGER_ACCOUNT_WORDING_LIST_URL
    item_route_name = GENERAL_LEDGER_ACCOUNT_WORDING_LIST_ITEM_URL
    item_name = "Nom de compte"
    permission = PERMISSIONS["global.config_accounting_measure"]

    def stream_columns(self, account_wording):
        yield str(account_wording.account_number)
        yield str(account_wording.wording)

    def load_items(self):
        items = self.factory.query()
        items = items.order_by(asc(self.factory.account_number))
        return items

    def stream_actions(self, account_wording):
        """
        Stream the actions available for the given measure_type object
        :param obj measure_type: TreasuryMeasureType instance
        :returns: List of 4-uples (url, label, title, icon,)
        """
        yield Link(
            self._get_item_url(account_wording), "Modifier", icon="pen", css="icon"
        )
        yield POSTButton(
            self._get_item_url(account_wording, action="delete"),
            "Supprimer le nom du compte",
            title="Le nom du compte sera définitivement supprimé",
            icon="trash-alt",
            css="icon, negative",
        )


class GeneralLedgerAccountWordingAddView(BaseAdminAddView):
    title = "Ajouter un nom de compte"
    route_name = GENERAL_LEDGER_ACCOUNT_WORDING_LIST_URL
    factory = GeneralLedgerAccountWording
    schema = get_admin_general_ledger_account_wording_schema(
        GeneralLedgerAccountWording
    )
    permission = PERMISSIONS["global.config_accounting_measure"]


class GeneralLedgerAccountWordingEditView(BaseAdminEditView):
    title = "Modifier un nom de compte"
    route_name = GENERAL_LEDGER_ACCOUNT_WORDING_LIST_ITEM_URL
    factory = GeneralLedgerAccountWording
    schema = get_admin_general_ledger_account_wording_schema(
        GeneralLedgerAccountWording
    )
    permission = PERMISSIONS["global.config_accounting_measure"]


class GeneralLedgerAccountWordingDeleteView(BaseAdminDeleteView):
    route_name = GENERAL_LEDGER_ACCOUNT_WORDING_LIST_ITEM_URL
    permission = PERMISSIONS["global.config_accounting_measure"]


def add_routes(config):
    """
    Add routes related to this module
    """
    config.add_route(BASE_URL, BASE_URL)
    config.add_route(
        GENERAL_LEDGER_ACCOUNT_SETTING_URL, GENERAL_LEDGER_ACCOUNT_SETTING_URL
    )
    config.add_route(
        GENERAL_LEDGER_ACCOUNT_WORDING_LIST_URL, GENERAL_LEDGER_ACCOUNT_WORDING_LIST_URL
    )
    config.add_route(
        GENERAL_LEDGER_ACCOUNT_WORDING_LIST_ITEM_URL,
        GENERAL_LEDGER_ACCOUNT_WORDING_LIST_ITEM_URL,
        traverse="general_ledger_account_wordings_list/{id}",
    )


def add_views(config):
    """
    Add views defined in this module
    """
    config.add_admin_view(
        GeneralLedgerIndexView,
        parent=AccountingIndexView,
    )
    config.add_admin_view(
        GeneralLedgerAccountSettingView,
        parent=GeneralLedgerIndexView,
    )
    config.add_admin_view(
        GeneralLedgerAccountWordingListView,
        parent=GeneralLedgerIndexView,
        renderer="admin/crud_list.mako",
    )

    config.add_admin_view(
        GeneralLedgerAccountWordingAddView,
        parent=GeneralLedgerAccountWordingListView,
        renderer="admin/crud_add_edit.mako",
        request_param="action=add",
    )
    config.add_admin_view(
        GeneralLedgerAccountWordingEditView,
        parent=GeneralLedgerAccountWordingListView,
        renderer="admin/crud_add_edit.mako",
    )

    config.add_admin_view(
        GeneralLedgerAccountWordingDeleteView,
        parent=GeneralLedgerAccountWordingListView,
        request_param="action=delete",
        require_csrf=True,
        request_method="POST",
    )


def includeme(config):
    add_routes(config)
    add_views(config)

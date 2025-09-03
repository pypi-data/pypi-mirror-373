"""
Admin view for accounting closure related settings
"""

import logging
import os
import datetime

from sqlalchemy import asc

from caerp.consts.permissions import PERMISSIONS
from caerp.forms.admin import get_config_schema
from caerp.views.admin.accounting import (
    AccountingIndexView,
    ACCOUNTING_URL,
)
from caerp.models.accounting.accounting_closures import AccountingClosure

from caerp.forms.accounting import get_admin_accounting_closure_schema

from caerp.utils.widgets import (
    POSTButton,
)

from caerp.views.admin.tools import (
    AdminCrudListView,
    BaseConfigView,
    BaseAdminIndexView,
    BaseAdminAddView,
    BaseAdminDisableView,
)

logger = logging.getLogger(__name__)


BASE_URL = os.path.join(ACCOUNTING_URL, "accounting_closure")
CLOSURE_SETTINGS_URL = os.path.join(BASE_URL, "closure_settings")

CLOSURE_LIST_URL = os.path.join(BASE_URL, "closure_list")
CLOSURE_LIST_ITEM_URL = CLOSURE_LIST_URL + "/{id}"


class AccountingClosureIndexView(BaseAdminIndexView):
    title = "Clôtures comptables"
    description = "Paramétrer et clôturer les exercices comptables"
    route_name = BASE_URL
    permission = PERMISSIONS["global.config_accounting"]


class AccountingClosureSettingsView(BaseConfigView):
    title = "Paramètres des exercices comptables"
    description = "Paramétrer le jour et le mois de fin des exercices comptables"
    route_name = CLOSURE_SETTINGS_URL
    redirect_route_name = BASE_URL

    validation_msg = "Les informations ont bien été enregistrées"
    info_message = "Afin qu'enDI puisse calculer correctement les états de trésorerie \
    des entrepreneurs, le jour et le mois de fin d'exercice comptable doivent \
    être paramétré. Si rien n'est paramétré, le 31/12 est utilisé."
    keys = (
        "accounting_closure_day",
        "accounting_closure_month",
    )
    schema = get_config_schema(keys)
    permission = PERMISSIONS["global.config_accounting"]


class AccountingClosureListView(AdminCrudListView):
    title = "Clôturer les exercices"
    description = "Permet de clôturer définitivement les exercices passés"
    columns = [
        "Année de fin de l'exercice",
        "Clôturé ?",
        "Date et heure de la clôture",
    ]
    factory = AccountingClosure
    route_name = CLOSURE_LIST_URL
    item_route_name = CLOSURE_LIST_ITEM_URL
    item_name = "Clôtures comptables"
    permission = PERMISSIONS["global.config_accounting"]

    def stream_columns(self, accounting_closure):
        yield str(accounting_closure.year)
        if accounting_closure.active:
            yield str("Oui")
        else:
            yield str("Non")
        if accounting_closure.datetime:
            yield str(accounting_closure.datetime)
        else:
            yield ""

    def load_items(self):
        items = self.factory.query()
        items = items.order_by(asc(self.factory.year))
        return items

    def stream_actions(self, accounting_closure):
        """
        Stream the actions available for the given measure_type object
        :param obj measure_type: TreasuryMeasureType instance
        :returns: List of 4-uples (url, label, title, icon,)
        """
        if not accounting_closure.active:
            yield POSTButton(
                self._get_item_url(accounting_closure, action="close"),
                "Clôturer définitivement",
                title="L'exercice fiscal sera clôturé définitivement (impossible de revenir en arrière)",
                icon="lock",
                css="icon",
                confirm="Êtes vous sûr de vouloir clôturer cet exercice fiscal ? Attention, la clôture est définitive et irréversible !",
            )


class AccountingClosureAddView(BaseAdminAddView):
    title = "Ajouter un exercice fiscal"
    route_name = CLOSURE_LIST_URL
    factory = AccountingClosure
    schema = get_admin_accounting_closure_schema(AccountingClosure)
    permission = PERMISSIONS["global.config_accounting"]


class AccountingClosureCloseView(BaseAdminDisableView):
    route_name = CLOSURE_LIST_ITEM_URL
    factory = AccountingClosure
    permission = PERMISSIONS["global.config_accounting"]

    def on_disable(self):
        raise Forbidden("Interdiction de déclôturer une année")

    def on_enable(self):
        self.context.datetime = datetime.datetime.now()
        self.request.dbsession.merge(self.context)


def add_routes(config):
    """
    Add the routes related to the current module
    """
    config.add_route(BASE_URL, BASE_URL)
    config.add_route(CLOSURE_SETTINGS_URL, CLOSURE_SETTINGS_URL)
    config.add_route(CLOSURE_LIST_URL, CLOSURE_LIST_URL)
    config.add_route(
        CLOSURE_LIST_ITEM_URL,
        CLOSURE_LIST_ITEM_URL,
        traverse="closure_list/{id}",
    )


def add_views(config):
    """
    Add views defined in this module
    """
    config.add_admin_view(
        AccountingClosureIndexView,
        parent=AccountingIndexView,
    )
    config.add_admin_view(
        AccountingClosureSettingsView,
        parent=AccountingClosureIndexView,
    )
    config.add_admin_view(
        AccountingClosureListView,
        parent=AccountingClosureIndexView,
        renderer="admin/accounting_closure_crud_list.mako",
    )
    config.add_admin_view(
        AccountingClosureAddView,
        parent=AccountingClosureListView,
        renderer="admin/crud_add_edit.mako",
        request_param="action=add",
    )
    config.add_admin_view(
        AccountingClosureCloseView,
        parent=AccountingClosureListView,
        request_param="action=close",
        require_csrf=True,
        request_method="POST",
    )


def includeme(config):
    add_routes(config)
    add_views(config)

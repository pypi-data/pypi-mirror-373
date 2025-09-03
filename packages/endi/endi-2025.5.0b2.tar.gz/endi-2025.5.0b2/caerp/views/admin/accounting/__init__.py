import os

from caerp.consts.permissions import PERMISSIONS
from caerp.views.admin import (
    AdminIndexView,
    BASE_URL,
)
from caerp.views.admin.tools import BaseAdminIndexView


ACCOUNTING_URL = os.path.join(BASE_URL, "accounting")


class AccountingIndexView(BaseAdminIndexView):
    route_name = ACCOUNTING_URL
    title = "Module Comptabilité"
    description = "Configurer les tableaux de bord (trésorerie, \
comptes de résultat) et les paramètres liés au logiciel de comptabilité."
    permission = PERMISSIONS["global.config_accounting"]


def includeme(config):
    config.add_route(ACCOUNTING_URL, ACCOUNTING_URL)
    config.add_admin_view(AccountingIndexView, parent=AdminIndexView)
    config.include(".accounting_software")
    config.include(".treasury_measures")
    config.include(".balance_sheet_measures")
    config.include(".income_statement_measures")
    config.include(".accounting_closure")
    config.include(".company_general_ledger")
    config.include(".exports")

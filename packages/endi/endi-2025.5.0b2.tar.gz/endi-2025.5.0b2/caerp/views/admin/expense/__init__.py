import os

from caerp.consts.permissions import PERMISSIONS
from caerp.views.admin import (
    AdminIndexView,
    BASE_URL,
)
from caerp.views.admin.tools import BaseAdminIndexView


EXPENSE_URL = os.path.join(BASE_URL, "expenses")


class ExpenseIndexView(BaseAdminIndexView):
    route_name = EXPENSE_URL
    title = "Module Notes de dépenses"
    description = "Configurer les types de dépenses, les exports comptables"
    permission = PERMISSIONS["global.config_accounting"]


def includeme(config):
    config.add_route(EXPENSE_URL, EXPENSE_URL)
    config.add_admin_view(
        ExpenseIndexView,
        parent=AdminIndexView,
    )
    config.include(".types")
    config.include(".accounting")
    config.include(".numbers")

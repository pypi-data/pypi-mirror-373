"""
Entry point for caerp-solo specific stuff
"""
from caerp.consts.permissions import PERMISSIONS
from caerp.models.company import Company
from caerp.panels.menu import get_usermenu
from caerp.utils.menu import (
    AppMenuDropDown,
    AppMenuItem,
)
from caerp.utils.widgets import Link
from caerp.models.expense import ExpenseSheet
from caerp.views.expenses.lists import ExpenseList


def menu_panel(context, request):
    """
    Top menu panel

    Build the top menu dict representation

    :rtype: dict
    """
    # If we've no user in the current request, we don't return anything
    if not request.identity:
        return {}
    company = Company.query().first()
    menu_builder = request.registry.admin_menu
    menu = menu_builder.build(
        request,
        context=company,
        user_id=request.identity.id,
        company_id=company.id if company else None,
        submenu=False,
        is_user_company=True,
        company=company,
    )

    usermenu = get_usermenu(request)

    return {
        "menu": menu,
        "usermenu": usermenu,
    }


def hack_admin_menu(config):
    # On créé un menu "Solo" basé sur le menu d'enseigne
    solo_menu = config.registry.company_menu
    # On retire les entrées inutiles
    solo_menu.remove(solo_menu.find("accounting"))
    solo_menu.remove(solo_menu.find("document"))
    solo_menu.remove(solo_menu.find("accompagnement"))
    # On créé une entrée "Administration"
    solo_menu.add(AppMenuDropDown(name="admin", label="Administration"))
    # On y insère l'item "Configuration" issu du menu d'admin
    solo_menu.add(config.registry.admin_menu.items[1], "admin")
    # On renomme l'item "Annuaire" et on le déplace dans "Administration"
    users_item_index = solo_menu.items.index(solo_menu.find("users"))
    solo_menu.items[users_item_index].label = "Utilisateurs"
    solo_menu.add(solo_menu.items.pop(users_item_index), "admin")
    # On déplace l'item "Mon enseigne" dans "Administration"
    company_item_index = solo_menu.items.index(solo_menu.find("company"))
    solo_menu.add(solo_menu.items.pop(company_item_index), "admin")
    # On insère les items "Comptabilité" et "Suivi de gestion" issu du menu d'admin
    solo_menu.add(config.registry.admin_menu.find("accounting"))
    solo_menu.add(config.registry.admin_menu.find("management"))
    solo_menu.add(config.registry.admin_menu.find("training"))
    # On y créé un item "Export massif"
    solo_menu.add(
        AppMenuItem(label="Export massif des factures", href="/invoices/export/pdf"),
        "accounting",
    )
    # On remplace le menu d'admin par le nouveau menu "Solo"
    config.registry.admin_menu = solo_menu


def submenu_panel(context, request):
    return {}


class SoloExpenseList(ExpenseList):
    def stream_main_actions(self):
        company = Company.query().first()
        cid = company.id
        yield Link(
            self.request.route_path(
                "user_expenses", id=cid, uid=self.request.identity.id
            ),
            "Ajouter<span class='no_mobile'>&nbsp;une note de dépenses</span>",
            title="Ajouter une nouvelle note de dépenses",
            icon="plus",
            css="btn btn-primary",
        )

    def filter_status(self, query, appstruct):
        # Must add invalid and notpaid status
        status = appstruct.get("status")
        if status in ("wait", "valid", "invalid"):
            query = query.filter(ExpenseSheet.status == status)
        elif status in ("paid", "resulted"):
            query = query.filter(ExpenseSheet.status == "valid")
            query = query.filter(ExpenseSheet.paid_status == status)
        elif status == "notpaid":
            query = query.filter(ExpenseSheet.status == "valid")
            query = query.filter(ExpenseSheet.paid_status == "waiting")

        return query


def includeme(config):
    hack_admin_menu(config)
    config.add_panel(
        menu_panel,
        "menu",
        renderer="/panels/menu.mako",
    )
    config.add_panel(
        submenu_panel,
        "submenu",
        renderer="/panels/menu.mako",
    )
    config.add_view(
        SoloExpenseList,
        route_name="expenses",
        permission=PERMISSIONS["global.list_expenses"],
        renderer="expenses/admin_expenses.mako",
    )
    config.add_view(
        SoloExpenseList,
        route_name="company_expenses",
        permission=PERMISSIONS["global.list_expenses"],
        renderer="expenses/admin_expenses.mako",
    )

from caerp.consts.permissions import PERMISSIONS
from collections import namedtuple
import logging
from typing import Dict, Optional


from pyramid.decorator import reify
from pyramid.httpexceptions import HTTPFound

from caerp.models.company import Company
from caerp.models.user.user import User
from caerp.utils.widgets import (
    ViewLink,
    Link,
    POSTButton,
)

from caerp.views import (
    BaseView,
    add_panel_view,
    DisableView,
    JsAppViewMixin,
)
from caerp.views.render_api import format_account
from caerp.views.third_party.customer.routes import COMPANY_CUSTOMERS_ADD_ROUTE
from caerp.views.supply.invoices.routes import (
    COMPANY_COLLECTION_ROUTE as COMPANY_SUPPLIER_INVOICES_COLLECTION_ROUTE,
)
from caerp.views.user.routes import (
    USER_LOGIN_URL,
    USER_URL,
)
from caerp.resources import (
    dashboard_resources,
    node_view_only_js,
)

from caerp.models.accounting.bookeeping import CustomInvoiceBookEntryModule

from .tools import get_company_url

from .routes import (
    API_ROUTE,
    API_ITEM_ROUTE,
    COLLECTION_ROUTE,
    ITEM_ROUTE,
    DASHBOARD_ROUTE,
    COMPANY_ESTIMATION_ADD_ROUTE,
    COMPANY_INVOICE_ADD_ROUTE,
)


logger = logging.getLogger(__name__)


ENABLE_MSG = "L'enseigne {0} a été (ré)activée."
DISABLE_MSG = "L'enseigne {0} a été désactivée."

ENABLE_ERR_MSG = "Erreur à l'activation de l'enseigne {0}."
DISABLE_ERR_MSG = "Erreur à la désactivation de l'enseigne {0}."


ShortcutButton = namedtuple("ShortcutButton", ["url", "icon", "text", "title"])


def get_enabled_bookeeping_modules() -> dict:
    """
    List enabled bookeeping modules
    """
    enabled_modules = {}
    for prefix in ("", "internal"):
        for module in ("contribution", "insurance"):
            key = "{}{}".format(prefix, module)
            enabled_modules[key] = (
                CustomInvoiceBookEntryModule.get_by_name(module, prefix) is not None
            )
    return enabled_modules


def _get_company_shortcuts(company, request) -> dict:
    """
    Collect shortcuts for the company dashboard
    """
    buttons = []
    msg = ""
    if company.customers:
        if company.projects:
            buttons.append(
                ShortcutButton(
                    url=request.route_path(
                        COMPANY_ESTIMATION_ADD_ROUTE,
                        id=company.id,
                    ),
                    icon="file-list",
                    text="Créer un devis",
                    title="Créer un nouveau devis",
                )
            )
            if request.has_permission(PERMISSIONS["context.add_invoice"], company):
                buttons.append(
                    ShortcutButton(
                        url=request.route_path(
                            COMPANY_INVOICE_ADD_ROUTE,
                            id=company.id,
                        ),
                        icon="file-invoice-euro",
                        text="Créer une facture",
                        title="Créer une nouvelle facture",
                    )
                )
        else:
            msg = "Ajoutez un dossier qui contiendra des devis et factures"
    else:
        msg = "Pour commencer, ajoutez un client"

    if len(company.employees) == 1 or request.identity in company.employees:
        if request.identity in company.employees:
            expense_user = request.identity
        else:
            # EA externe à l'enseigne
            expense_user = company.employees[0]

        buttons.append(
            ShortcutButton(
                url=request.route_path(
                    "user_expenses",
                    id=company.id,
                    uid=expense_user.id,
                ),
                icon="credit-card",
                text="Créer une note de dépense",
                title="Créer une nouvelle note de dépense",
            )
        ),
    # EA externe + multi-employés : on affiche pas le bouton.
    if request.has_module("supply.invoices"):
        buttons.append(
            ShortcutButton(
                url=request.route_path(
                    COMPANY_SUPPLIER_INVOICES_COLLECTION_ROUTE,
                    id=company.id,
                    _query=dict(action="new"),
                ),
                icon="box-euro",
                text="Créer une facture fournisseur",
                title="Créer une nouvelle facture fournisseur",
            )
        )

    if company.customers:
        buttons.append(
            ShortcutButton(
                url=request.route_path(
                    "/companies/{id}/projects",
                    id=company.id,
                    _query=dict(action="add"),
                ),
                icon="folder",
                text="Ajouter un dossier",
                title="Ajouter un nouveau dossier",
            )
        )

    buttons.append(
        ShortcutButton(
            url=request.route_path(
                COMPANY_CUSTOMERS_ADD_ROUTE,
                id=company.id,
            ),
            icon="user",
            text="Ajouter un client",
            title="Ajouter un nouveau client",
        )
    )
    return dict(
        shortcuts_msg=msg,
        shortucts_buttons=buttons,
    )


def company_dashboard(request):
    """
    index page for the company shows latest news :
        - last validated estimation/invoice
        - To be relaunched bill
        - shortcut buttons
    """
    dashboard_resources.need()
    company = request.context

    shortcuts = _get_company_shortcuts(company, request)

    ret_val = dict(
        title=company.name.title(),
        company=company,
        elapsed_invoices=request.context.get_late_invoices(),
    )
    ret_val.update(shortcuts)
    return ret_val


class CompanyView(JsAppViewMixin, BaseView):
    def context_url(self, _query: Dict[str, str] = {}):
        return get_company_url(self.request, api=True, **_query)

    def __call__(self):
        request = self.request
        company = request.context

        populate_actionmenu(request)
        node_view_only_js.need()

        actions = []
        if request.has_permission(PERMISSIONS["context.edit_company"]):
            actions.append(
                Link(
                    get_company_url(request, action="edit"),
                    "Modifier",
                    title="Modifier l´enseigne",
                    icon="pen",
                    css="btn btn-primary icon",
                )
            )

        if request.has_permission(PERMISSIONS["global.create_company"]):
            url = get_company_url(request, action="disable")
            if company.active:
                actions.append(
                    POSTButton(
                        url,
                        "Désactiver",
                        title="Désactiver l'enseigne",
                        icon="lock",
                        css="icon",
                    )
                )
            else:
                actions.append(
                    POSTButton(
                        url,
                        "Activer",
                        title="Activer l'enseigne",
                        icon="lock-open",
                        css="icon",
                    )
                )

        return dict(
            title=company.name.title(),
            company=company,
            actions=actions,
            enabled_modules=get_enabled_bookeeping_modules(),
            js_app_options=self.get_js_app_options(),
        )


class CompanyDisableView(DisableView):
    def on_disable(self):
        """
        Disable logins of users that are only attached to this company
        """
        for user in self.context.employees:
            other_enabled_companies = [
                company
                for company in user.companies
                if company.active and company.id != self.context.id
            ]
            if (
                getattr(user, "login")
                and user.login.active
                and len(other_enabled_companies) == 0
            ):
                user.login.active = False
                self.request.dbsession.merge(user.login)
                user_url = self.request.route_path(USER_LOGIN_URL, id=user.id)
                self.request.session.flash(
                    "Les identifiants de <a href='{0}'>{1}</a> ont été        "
                    "             désactivés".format(user_url, user.label)
                )

    def redirect(self):
        return HTTPFound(self.request.referrer)


def set_company_image(company, appstruct):
    for fname in ("header", "logo"):
        if fname in appstruct:
            setattr(company, fname, appstruct.get(fname, {}))


class CompanyAdd(BaseView, JsAppViewMixin):
    """
    View class for company add

    JS view, the form/submit stuff is handled via vuejs and REST API.

    Have support for a user_id request param that allows to add the user
    directly on company creation

    """

    title = "Ajouter une enseigne"

    def context_url(self, _query: dict = {}):
        return self.request.route_path(API_ROUTE, _query=_query)

    def __call__(self) -> dict:
        from caerp.resources import company_js

        company_js.need()
        result = {
            "title": self.title,
            "js_app_options": self.get_js_app_options(),
        }
        return result


class CompanyEdit(CompanyAdd):
    """
    View class for company editing

    JS view, the form/submit stuff is handled via vuejs and REST API.
    """

    @reify
    def title(self):
        """
        title property
        """
        return "Modification de {0}".format(self.context.name.title())

    def context_url(self, _query={}):
        return self.request.route_path(
            API_ITEM_ROUTE, id=self.context.id, _query=_query
        )

    def more_js_app_options(self):
        result = super().more_js_app_options()
        result["company_id"] = self.context.id
        return result

    def redirect(self, appstruct):
        return HTTPFound(get_company_url(self.request))


def populate_actionmenu(request, company=None):
    """
    add item in the action menu
    """
    request.actionmenu.add(get_list_view_btn())
    if company is not None:
        request.actionmenu.add(get_view_btn(company.id))


def get_list_view_btn():
    """
    Return a link to the CAE's directory
    """
    return ViewLink("Annuaire", "visit", path=USER_URL)


def get_view_btn(company_id):
    """
    Return a link to the view page
    """
    return ViewLink("Fiche de l’enseigne", "visit", path=ITEM_ROUTE, id=company_id)


def company_remove_employee_view(context, request):
    """
    Enlève un employé de l'enseigne courante
    """
    uid = request.params.get("uid")
    if not uid:
        request.session.flash("Missing uid parameter", "error")
    else:
        user = User.get(uid)
        if not user:
            request.session.flash("User not found", "error")

        if user in context.employees:
            context.employees = [
                employee for employee in context.employees if employee != user
            ]
            request.session.flash(
                "L'utilisateur {0} ne fait plus partie de l'enseigne {1}".format(
                    format_account(user), context.name
                )
            )
    url = request.referer
    if url is None:
        url = get_company_url(request)
    return HTTPFound(url)


def includeme(config):
    config.add_view(
        CompanyAdd,
        route_name=COLLECTION_ROUTE,
        renderer="base/vue_app.mako",
        request_param="action=add",
        permission=PERMISSIONS["global.create_company"],
        layout="vue_opa",
    )
    config.add_view(
        company_dashboard,
        route_name=DASHBOARD_ROUTE,
        renderer="company_index.mako",
        permission=PERMISSIONS["company.view"],
        context=Company,
    )
    config.add_view(
        company_dashboard,
        route_name=ITEM_ROUTE,
        renderer="company_index.mako",
        request_param="action=index",
        permission=PERMISSIONS["company.view"],
        context=Company,
    )
    config.add_view(
        CompanyView,
        route_name=ITEM_ROUTE,
        renderer="company/company.mako",
        permission=PERMISSIONS["global.authenticated"],
        context=Company,
    )
    config.add_view(
        CompanyEdit,
        route_name=ITEM_ROUTE,
        renderer="base/vue_app.mako",
        request_param="action=edit",
        permission=PERMISSIONS["context.edit_company"],
        layout="vue_opa",
        context=Company,
    )
    config.add_view(
        CompanyDisableView,
        route_name=ITEM_ROUTE,
        request_param="action=disable",
        permission=PERMISSIONS["global.create_company"],
        require_csrf=True,
        request_method="POST",
        context=Company,
    )
    config.add_view(
        company_remove_employee_view,
        route_name=ITEM_ROUTE,
        request_param="action=remove",
        permission=PERMISSIONS["global.create_company"],
        require_csrf=True,
        request_method="POST",
        context=Company,
    )
    # same panel as html view
    for panel, request_param in (
        (
            "company_recent_tasks",
            "action=tasks_html",
        ),
        (
            "company_coming_events",
            "action=events_html",
        ),
    ):
        add_panel_view(
            config,
            panel,
            route_name=ITEM_ROUTE,
            request_param=request_param,
            permission=PERMISSIONS["company.view"],
            context=Company,
        )

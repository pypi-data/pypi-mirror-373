import logging
from caerp.consts.permissions import PERMISSIONS
from caerp.default_layouts import DefaultLayout

from caerp.resources import (
    user_resources,
)
from caerp.models.user.user import User
from caerp.utils.menu import (
    MenuItem,
    AttrMenuItem,
    Menu,
)
from caerp.views.user.routes import (
    USER_ITEM_URL,
    USER_LOGIN_URL,
    USER_ACCOUNTING_URL,
)

logger = logging.getLogger(__name__)


def deferred_enterprise_label(item, kw):
    """
    Collect a custom label for the "Enseignes" menu entry using binding
    parameters
    """
    current_user = kw["current_user"]
    if current_user.companies:
        label = "Enseignes <span class='bubble'>{}</span>".format(
            len(current_user.companies)
        )
    else:
        label = "<em>Enseignes</em> <span class='bubble negative'>0</span>"
    return label


def deferred_login_label(item, kw):
    """
    Custom deferred label for the login sidebar entry
    """
    current_user = kw["current_user"]
    if current_user.login:
        return "Identifiants et droits"
    else:
        return "<em>Identifiants et droits</em>"


def deferred_accounting_show_perm(item, kw):
    request = kw["request"]
    current_user = kw["current_user"]
    if current_user.login:
        return request.has_permission(PERMISSIONS["global.manage_accounting"])
    else:
        return False


UserMenu = Menu(name="usermenu")

UserMenu.add(
    MenuItem(
        name="user",
        label="Compte utilisateur",
        route_name=USER_ITEM_URL,
        icon="user",
        perm=PERMISSIONS["context.view_user"],
    )
)
UserMenu.add(
    AttrMenuItem(
        name="login",
        label=deferred_login_label,
        route_name=USER_LOGIN_URL,
        icon="lock",
        disable_attribute="login",
        perm_context_attribute="login",
        perm=PERMISSIONS["global.create_user"],
    ),
)
UserMenu.add(
    AttrMenuItem(
        name="accounting",
        label="Informations comptables",
        route_name=USER_ACCOUNTING_URL,
        icon="euro-circle",
        perm=deferred_accounting_show_perm,
    )
)
UserMenu.add(
    AttrMenuItem(
        name="companies",
        label=deferred_enterprise_label,
        title="Enseignes associées à ce compte",
        route_name="/users/{id}/companies",
        icon="building",
        perm=PERMISSIONS["global.company_view"],
    ),
)


class UserLayout(DefaultLayout):
    """
    Layout for user related pages
    Provide the main page structure for user view
    """

    def __init__(self, context, request):
        super().__init__(context, request)
        user_resources.need()

        if isinstance(context, User):
            self.current_user_object = context
        elif hasattr(context, "user"):
            self.current_user_object = context.user
        elif hasattr(context, "userdatas"):
            self.current_user_object = context.userdatas.user
        else:
            raise KeyError(
                "Can't retrieve the associated user object, \
                           current context : %s"
                % context
            )

    @property
    def usermenu(self):
        UserMenu.set_current(self.current_user_object)
        UserMenu.bind(current_user=self.current_user_object)
        return UserMenu


def includeme(config):
    config.add_layout(
        UserLayout, template="caerp:templates/user/layout.mako", name="user"
    )

import logging

import colander
from colanderalchemy import SQLAlchemySchemaNode
from deform_extensions import GridFormWidget
from pyramid.httpexceptions import HTTPBadRequest, HTTPFound

from caerp.consts.permissions import PERMISSIONS
from caerp.consts.users import ACCOUNT_TYPES_LABELS
from caerp.controllers.user.login import change_login_account_type
from caerp.forms.user.login import get_add_edit_schema, get_password_schema
from caerp.models.user import User
from caerp.services.user.login import get_last_connection
from caerp.utils.strings import format_account
from caerp.utils.widgets import POSTButton
from caerp.views import BaseFormView, DeleteView, DisableView
from caerp.views.user.routes import (
    USER_ITEM_URL,
    USER_LOGIN_ADD_URL,
    USER_LOGIN_DISABLE_URL,
    USER_LOGIN_EDIT_URL,
    USER_LOGIN_SET_PASSWORD_URL,
    USER_LOGIN_URL,
)
from caerp.views.user.tools import UserFormConfigState

logger = logging.getLogger(__name__)

LOGIN_GRID = (
    (("login", 12),),
    (("password", 12),),
    (("pwd_hash", 12),),
    (("account_type", 12),),
    (("groups", 12),),
    (("estimation_limit_amount", 6), ("invoice_limit_amount", 6)),
    (("supplier_order_limit_amount", 6), ("supplier_invoice_limit_amount", 6)),
)


def user_login_view(context, request):
    """
    Return the login view datas
    """
    return dict(
        login=context.login,
        title="Identifiants rattachés au compte",
        last_connection=get_last_connection(request, context.id),
    )


class LoginAddView(BaseFormView):
    """
    View handling login add
    """

    add_template_vars = ("width",)

    @property
    def width(self):
        return "80"

    def __init__(self, *args, **kwargs):
        BaseFormView.__init__(self, *args, **kwargs)
        self.form_config = UserFormConfigState(self.session)

    @property
    def title(self):
        return "Ajouter des identifiants pour le compte {} ({})".format(
            self.context.label, self.context.email
        )

    def get_current_account_type(self):
        return self.form_config.get_default("account_type", "entrepreneur")

    def get_default_values(self):
        result = {
            "login": self.context.email,
            "user_id": self.context.id,
        }

        result["account_type"] = self.get_current_account_type()

        groups = self.form_config.get_default("groups", [])
        if groups:
            result["groups"] = groups
        return result

    def before(self, form):
        logger.debug(
            "In the login form, defaults {0}".format(self.form_config.get_defaults())
        )
        form.widget = GridFormWidget(named_grid=LOGIN_GRID)
        form.set_appstruct(self.get_default_values())

    def get_schema(self):
        account_type = self.get_current_account_type()
        return get_add_edit_schema(self.request, account_type=account_type)

    def submit_success(self, appstruct):
        password = appstruct.pop("pwd_hash", None)
        model = self.get_schema().objectify(appstruct)
        if "groups" in appstruct:
            groups = appstruct.pop("groups", [])
            groups = list(groups)
            logger.debug("  + Groups {0} added".format(groups))
            model.groups = groups

        model.user_id = self.context.id
        model.set_password(password)
        self.dbsession.add(model)
        self.dbsession.flush()

        next_step = self.form_config.get_next_step()
        # On fait le ménage dans les défauts transmis par les formulaires précédents
        self.form_config.pop_default("account_type", None)
        self.form_config.pop_default("groups", None)
        if next_step is not None:
            redirect = self.request.route_path(
                next_step,
                id=self.context.id,
            )
        else:
            redirect = self.request.route_path(
                USER_ITEM_URL,
                id=self.context.id,
            )
        logger.debug("  + Login  with id {0} added".format(model.id))
        return HTTPFound(redirect)


class UserLoginEditView(BaseFormView):
    add_template_vars = ("before_form_elements",)

    def current(self):
        return self.context.login

    def get_schema(self) -> SQLAlchemySchemaNode:
        return get_add_edit_schema(self.request, self.current().account_type, edit=True)

    def is_my_account_view(self):
        return self.current().user_id == self.request.identity.id

    @property
    def title(self):
        if self.is_my_account_view():
            return "Modification de mes identifiants"
        else:
            return "Modification des identifiants de {0}".format(
                format_account(self.current().user)
            )

    def before(self, form):
        form.widget = GridFormWidget(named_grid=LOGIN_GRID)
        form_fields = {
            "login": self.current().login,
            "account_type": self.current().account_type,
            "groups": self.current().groups,
            "user_id": self.current().user_id,
        }

        if self.current().supplier_order_limit_amount is not None:
            form_fields[
                "supplier_order_limit_amount"
            ] = self.current().supplier_order_limit_amount

        if self.current().supplier_invoice_limit_amount is not None:
            form_fields[
                "supplier_invoice_limit_amount"
            ] = self.current().supplier_invoice_limit_amount

        if self.current().estimation_limit_amount is not None:
            form_fields[
                "estimation_limit_amount"
            ] = self.current().estimation_limit_amount

        if self.current().invoice_limit_amount is not None:
            form_fields["invoice_limit_amount"] = self.current().invoice_limit_amount

        form.set_appstruct(form_fields)

    @property
    def before_form_elements(self):
        if self.request.has_permission(PERMISSIONS["global.create_user"]):
            return (
                POSTButton(
                    self.request.current_route_path(
                        _query="action=toggle_account_type"
                    ),
                    label="Compte entrepreneur",
                    title="Convertir ce compte en compte entrepreneur",
                    css_class="btn-default",
                    disabled=self.context.login.account_type == "entrepreneur",
                    extra_fields=[("account_type", "entrepreneur")],
                ),
                POSTButton(
                    self.request.current_route_path(
                        _query="action=toggle_account_type"
                    ),
                    label="Compte équipe d'appui",
                    title="Convertir ce compte en compte Équipe d'appui",
                    css_class="btn-default",
                    disabled=self.context.login.account_type == "equipe_appui",
                    extra_fields=[("account_type", "equipe_appui")],
                ),
                POSTButton(
                    self.request.current_route_path(
                        _query="action=toggle_account_type"
                    ),
                    label="Compte Hybride ES/EA",
                    title="Convertir ce compte en un compte Hybride ES/EA",
                    css_class="btn-default",
                    disabled=self.context.login.account_type == "hybride",
                    extra_fields=[("account_type", "hybride")],
                ),
            )
        else:
            return []

    def submit_success(self, appstruct):
        password = appstruct.pop("pwd_hash", None)
        model = self.get_schema().objectify(appstruct, self.current())
        if "groups" in appstruct:
            groups = appstruct.pop("groups", [])
            groups = list(groups)
            model.groups = groups
        if password:
            model.set_password(password)

        # Ensure values are positive numbers
        for limit in (
            "supplier_order_limit_amount",
            "supplier_invoice_limit_amount",
            "estimation_limit_amount",
            "invoice_limit_amount",
        ):
            if appstruct.get(limit, None) not in (None, colander.null):
                amount = appstruct.pop(limit)
                setattr(model, limit, abs(amount))

        self.dbsession.merge(model)
        self.dbsession.flush()
        redirect = self.request.route_path(
            USER_LOGIN_URL,
            id=self.current().user_id,
        )
        logger.debug("  + Login  with id {0} modified".format(model.id))
        return HTTPFound(redirect)


class UserLoginToggleAccountTypeView(BaseFormView):
    """
    Changer le type de compte
    """

    def get_schema(self):
        schema = colander.Schema()
        schema.add(
            colander.SchemaNode(
                colander.String(),
                name="account_type",
                validator=colander.OneOf(tuple(ACCOUNT_TYPES_LABELS.keys())),
            )
        )
        return schema

    @property
    def title(self):
        return "Changement de type de compte"

    def before(self, form):
        form.set_appstruct({"account_type": self.context.login.account_type})

    def __call__(self):
        schema = self.get_schema()
        try:
            data = schema.deserialize(self.request.POST)
        except colander.Invalid:
            logger.exception("Invalid input")
            raise HTTPBadRequest()
        else:
            login = self.context.login
            account_type = data["account_type"]
            login = change_login_account_type(self.request, login, account_type)
            redirect = self.request.route_path(
                USER_LOGIN_EDIT_URL,
                id=self.context.id,
            )
            logger.info(
                "  + Login  with id {0} account type changed to {1}".format(
                    login.id, login.account_type
                )
            )
            return HTTPFound(redirect)


class UserLoginPasswordView(UserLoginEditView):
    """
    Changer mon mot de passe
    """

    add_template_vars = ()

    def get_schema(self):
        return get_password_schema(self.request)

    @property
    def title(self):
        if self.is_my_account_view():
            return "Modification de mon mot de passe"
        else:
            return "Modification du mot de passe de {0}".format(
                format_account(self.current().user)
            )


class UserLoginDisableView(DisableView):
    def get_item(self):
        return self.context.login

    def on_disable(self):
        for company in self.context.companies:
            active_employees = [
                emp
                for emp in company.employees
                if emp and emp.login and emp.login.active and emp.id != self.context.id
            ]
            if company.active and not active_employees:
                company.disable()
                self.request.dbsession.merge(company)

    def redirect(self):
        return HTTPFound(
            self.request.route_path(
                USER_LOGIN_URL,
                id=self.context.id,
            )
        )


class LoginDeleteView(DeleteView):
    delete_msg = "Les identifiants ont bien été supprimés"

    def delete(self):
        self.request.dbsession.delete(self.context.login)

    def redirect(self):
        return HTTPFound(self.request.route_path(USER_ITEM_URL, id=self.context.id))


def includeme(config):
    config.add_view(
        user_login_view,
        route_name=USER_LOGIN_URL,
        renderer="/user/login.mako",
        layout="user",
        context=User,
        permission=PERMISSIONS["context.view_login"],
    )

    config.add_view(
        LoginAddView,
        route_name=USER_LOGIN_ADD_URL,
        renderer="/base/formpage.mako",
        layout="default",
        context=User,
        permission=PERMISSIONS["context.add_login"],
    )
    config.add_view(
        UserLoginEditView,
        route_name=USER_LOGIN_EDIT_URL,
        renderer="/user/edit.mako",
        layout="user",
        context=User,
        permission=PERMISSIONS["context.edit_login"],
    )
    config.add_view(
        UserLoginToggleAccountTypeView,
        route_name=USER_LOGIN_EDIT_URL,
        renderer="/user/edit.mako",
        layout="user",
        request_param="action=toggle_account_type",
        require_csrf=True,
        request_method="POST",
        context=User,
        permission=PERMISSIONS["global.create_user"],
    )
    config.add_view(
        UserLoginDisableView,
        route_name=USER_LOGIN_DISABLE_URL,
        layout="user",
        require_csrf=True,
        request_method="POST",
        context=User,
        permission=PERMISSIONS["context.edit_login"],
    )
    config.add_view(
        UserLoginPasswordView,
        route_name=USER_LOGIN_SET_PASSWORD_URL,
        renderer="/user/edit.mako",
        layout="user",
        context=User,
        permission=PERMISSIONS["context.edit_login"],
    )

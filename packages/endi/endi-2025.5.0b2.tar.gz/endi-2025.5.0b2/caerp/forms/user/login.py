"""
Login related form schemas

1- Password change
2- Add/Edit Form
3- Group configuration
"""
import functools
import logging
import colander
import deform

from sqlalchemy import select
from sqlalchemy.orm import load_only

from colanderalchemy import SQLAlchemySchemaNode

from caerp import forms
from caerp.models.user.group import Group
from caerp.models.user.user import User
from caerp.models.user.login import Login


logger = logging.getLogger(__name__)


def _get_unique_login_validator(login_id=None):
    """
    Return a unique login validator

        login_id

            The id of the current user in case we edit an account (the unicity
            should be checked on all the other accounts)
    """

    def unique_login(node, value):
        """
        Test login unicity against database
        """
        if not Login.unique_login(value, login_id):
            message = "Le login '{0}' n'est pas disponible.".format(value)
            raise colander.Invalid(node, message)

    return unique_login


@colander.deferred
def _deferred_login_validator(node, kw):
    """
    Dynamically choose the validator user for validating the login
    """
    context = kw["request"].context
    if isinstance(context, Login):
        login_id = context.id
    elif isinstance(context, User):
        login_id = context.login.id
    return _get_unique_login_validator(login_id)


def get_auth_validator(current_login_object=None):
    """
    Build an authentication validator

    :param obj current_login_object: If a login instance is provided use it for
    authentication
    """

    def auth_validator(form, value):
        """
        Authentication validator

        :param obj form: The form object
        :param dict value: The submitted datas to validate
        :raises: colander.Invalid on invalid authentication
        """
        logger.debug(" * Authenticating")
        if current_login_object is None:
            login = value.get("login")
            login_object = Login.find_by_login(login)
            logger.debug("   +  Login {0}".format(login))
        else:
            login_object = current_login_object
            logger.debug("   +  Login {0}".format(login_object.login))

        password = value.get("password")
        if not login_object or not login_object.auth(password):
            logger.error("    - Authentication : Error")
            message = "Erreur d'authentification"
            exc = colander.Invalid(form, message)
            exc["password"] = message
            raise exc
        else:
            logger.debug("   + Authentication : OK")

    return auth_validator


@colander.deferred
def deferred_password_validator(node, kw):
    context = kw["request"].context
    if isinstance(context, Login):
        login = context
    elif isinstance(context, User):
        login = context.login
    else:
        raise Exception("Invalid context for this validator")
    return get_auth_validator(login)


def get_groups(request, account_type=None):
    """
    Collect groups

    :returns: available groups as a list of 2-uples (name, label)
    """
    query = select(Group).options(
        load_only(Group.name, Group.label, Group.default_for_account_type)
    )
    if account_type and account_type != "hybride":
        query = query.filter(Group.account_type.in_([account_type, "all"]))

    if not request.has_permission("global.add_admin"):
        query = query.filter(Group.name != "admin")

    query = query.order_by(
        Group.default_for_account_type.desc(), Group.account_type, Group.label
    )

    groups = request.dbsession.scalars(query)
    return [group for group in groups]


def get_group_validator(request, groups):
    """
    Build a validator for group name validation


    :returns: A colander validator
    """
    validator = colander.ContainsOnly([group.name for group in groups])
    return validator


def get_group_widget(request, groups):
    """
    Build a select widget for groups

    :returns: A deform widget
    """
    return deform.widget.CheckboxChoiceWidget(
        values=[(group.name, group.label) for group in groups],
        values_descriptions=[
            ", ".join([right.label for right in group.access_rights])
            for group in groups
        ],
        has_column="large",
    )


def _get_unique_user_id_validator(login_id=None):
    """
    Build a unique user_id validator to ensure a user is linked to only one user

    :param int login_id: optionnal current login_id (in case of edit)
    """

    def unique_user_id(node, value):
        if not Login.unique_user_id(value, login_id):
            message = f"{value} est déjà utilisé par un autre utilisateur."
            raise colander.Invalid(node, message)

    return unique_user_id


@colander.deferred
def _deferred_user_id_validator(node, kw):
    """
    Dynamically choose the validator user for validating the user_id
    """
    context = kw["request"].context
    if isinstance(context, Login):
        login_id = context.id
    elif isinstance(context, User):
        login_id = context.login.id
    else:
        raise Exception("Invalid context for this validator")
    return _get_unique_user_id_validator(login_id)


def set_widgets(schema, account_type: str = None):
    """
    Set common widgets on the schema object

    :param obj schema: a colander schema
    :param str account_type: The type of account (entrepreneur or equipe_appui or hybride)
    """
    customize = functools.partial(forms.customize_field, schema)
    if "pwd_hash" in schema:
        customize(
            "pwd_hash",
            widget=deform.widget.CheckedPasswordWidget(
                attributes={
                    "autocomplete": "new-password",
                },
            ),
        )

    if "user_id" in schema:
        customize("user_id", widget=deform.widget.HiddenWidget())

    if "account_type" in schema:
        if account_type is not None:
            schema["account_type"].widget = deform.widget.HiddenWidget()
        else:
            schema["account_type"].widget = deform.widget.RadioChoiceWidget(
                values=[
                    ("entrepreneur", "Entrepreneur"),
                    ("equipe_appui", "Équipe d'appui"),
                ],
            )
            schema["account_type"].missing = colander.required
        schema["account_type"].validator = colander.OneOf(
            ["entrepreneur", "equipe_appui"]
        )
    return schema


def remove_actual_password_my_account(schema, kw):
    """
    Remove the actual password field if it's not the current_user's account
    """
    context = kw["request"].context
    if context not in (kw["request"].identity, kw["request"].identity.login):
        del schema["password"]
        del schema.validator


def get_password_schema(request):
    """
    Return the schema for user password change

    :returns: a colander Schema
    """
    schema = SQLAlchemySchemaNode(
        Login,
        includes=("pwd_hash",),
        title="",
    )
    set_widgets(schema)

    schema.insert(
        0,
        colander.SchemaNode(
            colander.String(),
            widget=deform.widget.PasswordWidget(),
            name="password",
            title="Mot de passe actuel",
            default="",
        ),
    )

    schema["pwd_hash"].title = "Nouveau mot de passe"
    schema.validator = deferred_password_validator
    schema.after_bind = remove_actual_password_my_account

    return schema


def get_add_edit_schema(request, account_type, edit=False):
    """
    Add a form schema for login add/edit

    :returns: A colander form schema
    """
    if edit:
        excludes = ("account_type",)
    else:
        excludes = ()

    if account_type == "equipe_appui":
        excludes += (
            "supplier_order_limit_amount",
            "supplier_invoice_limit_amount",
            "estimator_order_limit_amount",
            "invoice_limit_amount",
            "estimation_limit_amount",
        )  # type: ignore

    schema = SQLAlchemySchemaNode(Login, excludes=excludes)
    set_widgets(schema, account_type=account_type)

    groups = get_groups(request, account_type=account_type)
    default = []
    for group in groups:
        if group.default_for_account_type:
            default.append(group.name)

    schema.add(
        colander.SchemaNode(
            colander.Set(),
            name="groups",
            validator=get_group_validator(request, groups),
            widget=get_group_widget(request, groups),
            title="Rôles de l'utilisateur",
            default=default,
            preparer=forms.uniq_entries_preparer,
        )
    )

    if edit:
        schema["login"].validator = _deferred_login_validator
        schema["pwd_hash"].missing = colander.drop
        schema["user_id"].validator = _deferred_user_id_validator
    else:
        schema["user_id"].validator = _get_unique_user_id_validator()
        schema["login"].validator = _get_unique_login_validator()
    return schema


class BaseAuthSchema(colander.MappingSchema):
    """
    Base auth schema (sufficient for json auth)
    """

    login = colander.SchemaNode(
        colander.String(),
        title="Identifiant",
    )
    password = colander.SchemaNode(
        colander.String(),
        widget=deform.widget.PasswordWidget(),
        title="Mot de passe",
    )


class AuthSchema(BaseAuthSchema):
    """
    Schema for authentication form
    """

    nextpage = colander.SchemaNode(
        colander.String(),
        widget=deform.widget.HiddenWidget(),
        missing=colander.drop,
    )
    remember_me = colander.SchemaNode(
        colander.Boolean(),
        widget=deform.widget.CheckboxWidget(),
        label="Rester connecté",
        title="",
        missing=False,
    )


def get_auth_schema():
    """
    return the authentication form schema
    """
    return AuthSchema(title="", validator=get_auth_validator())


def get_json_auth_schema():
    """
    return the auth form schema in case of json auth
    """
    return BaseAuthSchema(validator=get_auth_validator())

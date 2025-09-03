"""
UserDatas add edit views
"""
import logging
from caerp.consts.permissions import PERMISSIONS
from pyramid.httpexceptions import HTTPFound

from deform_extensions import AccordionFormWidget
from js.deform import auto_need
from caerp.controllers.rgpd.inspect import get_inspector
from caerp.controllers.rgpd.user import rgpd_clean_user
from caerp.controllers.user.userdata import add_userdata_to_user
from caerp.models.user import User
from caerp.models.user.userdatas import (
    UserDatas,
    SocialDocTypeOption,
    UserDatasSocialDocTypes,
    get_default_cae_situation,
)
from caerp.forms.user.userdatas import (
    get_add_edit_schema,
    USERDATAS_FORM_GRIDS,
    get_doctypes_schema,
)
from caerp.utils.strings import (
    format_account,
)
from caerp.utils.menu import (
    AttrMenuDropdown,
)
from caerp.utils.widgets import Link, POSTButton
from caerp.views import (
    BaseFormView,
    BaseEditView,
    submit_btn,
    cancel_btn,
    DeleteView,
)
from caerp.views.user.routes import (
    USER_ITEM_URL,
    USER_ADD_URL,
)
from caerp.views.userdatas.routes import (
    USERDATAS_ADD_URL,
    USERDATAS_URL,
    USER_USERDATAS_URL,
    USER_USERDATAS_ADD_URL,
    USER_USERDATAS_DOCTYPES_URL,
    USER_USERDATAS_PY3O_URL,
    USER_USERDATAS_CAREER_PATH_URL,
)
from caerp.views.user.tools import UserFormConfigState


logger = logging.getLogger(__name__)


def userdatas_add_entry_point(context, request):
    """
    Entry point for userdatas add
    Record the userdatas form as next form urls

    The add process follows this stream :
        1- entry point
        2- user add form
        3- userdatas form
    """
    config = UserFormConfigState(request.session)
    config.set_steps([USER_USERDATAS_ADD_URL])
    config.set_defaults({"account_type": "entrepreneur"})
    return HTTPFound(request.route_path(USER_ADD_URL))


def userdatas_add_view(context, request):
    """
    Add userdatas to an existing User object

    :param obj context: The pyramid context (User instance)
    :param obj request: The pyramid request
    """
    add_userdata_to_user(request, context)
    return HTTPFound(
        request.route_path(
            USER_USERDATAS_URL,
            id=context.id,
        )
    )


def ensure_doctypes_rel(userdatas_id, request):
    """
    Ensure there is a UserDatasSocialDocTypes instance attaching each social doc
    type with the userdatas

    :param int userdatas_id: The id of the userdatas instance
    :param obj request: The request object
    """
    for doctype in SocialDocTypeOption.query():
        doctype_id = doctype.id
        rel = UserDatasSocialDocTypes.get(
            (
                userdatas_id,
                doctype_id,
            )
        )
        if rel is None:
            rel = UserDatasSocialDocTypes(
                userdatas_id=userdatas_id,
                doctype_id=doctype_id,
            )
            request.dbsession.add(rel)
    request.dbsession.flush()


class UserUserDatasEditView(BaseEditView):
    """
    User datas edition view
    """

    buttons = (
        submit_btn,
        cancel_btn,
    )
    add_template_vars = (
        "current_userdatas",
        "get_buttons",
    )

    @property
    def title(self):
        return "Fiche de gestion sociale de {0}".format(
            format_account(self.context, False)
        )

    @property
    def current_userdatas(self):
        return self.context.userdatas

    @property
    def delete_url(self):
        return self.request.route_path(
            USER_USERDATAS_URL,
            id=self.context.id,
            _query={"action": "delete"},
        )

    def get_delete_button(self):
        return POSTButton(
            url=self.delete_url,
            label="Supprimer",
            title="Supprimer la fiche de gestion sociale",
            icon="trash-alt",
            css="icon negative",
            confirm=(
                "En supprimant cette fiche de gestion sociale, vous supprimerez"
                " également les informations qui y sont rattachées (documents "
                "sociaux, historiques, parcours). Continuer ?"
            ),
        )

    def get_anonymize_button(self):
        return Link(
            url=self.request.route_path(
                USER_USERDATAS_URL,
                id=self.context.id,
                _query={"action": "anonymize"},
            ),
            label="[RGPD] Anonymiser",
            title="Anonymiser les données de la fiche de gestion sociale",
            icon="mask",
            css="btn negative",
        )

    def get_buttons(self):
        if self.request.has_permission("context.delete_userdata"):
            if self.request.has_permission("global.rgpd_management"):
                yield self.get_anonymize_button()
            yield self.get_delete_button()

    def get_schema(self):
        return get_add_edit_schema(self.request)

    def before(self, form):
        BaseEditView.before(self, form)
        auto_need(form)
        form.widget = AccordionFormWidget(
            named_grids=USERDATAS_FORM_GRIDS, fallback_down=True
        )

    def get_context_model(self):
        return self.current_userdatas

    def redirect(self, appstruct):
        return HTTPFound(self.request.current_route_path())


class UserUserDatasDeleteView(DeleteView):
    def redirect(self):
        if not getattr(self, "delete_user", False):
            return HTTPFound(self.request.route_path(USER_ITEM_URL, id=self.context.id))
        return HTTPFound(self.request.route_path(USERDATAS_URL))

    def delete(self):
        self.dbsession.delete(self.context.userdatas)
        self.delete_user = False
        if not self.context.login and not self.context.companies:
            self.delete_user = True
            self.dbsession.delete(self.context)
            self.dbsession.flush()


def userdata_anonymize_view(context, request):
    """Anonymize userdatas and delete associated documents"""
    if "csrf_token" in request.POST:
        logger.debug(f"# Anonymisation de {context.label} : {context.id}")
        rgpd_clean_user(request, request.context)
        request.session.flash("Les données de gestion sociale ont été anonymisées")
        return HTTPFound(request.route_path(USER_USERDATAS_URL, id=context.id))
    inspector = get_inspector(UserDatas)
    fields = ""
    for column in inspector.columns:
        fields += f"<li class='{column['key']}'>{column['label']}</li>"
    return {
        "title": f"Anonymisation des données de gestion sociale de {context.label}",
        "confirmation_message": (
            "<p>En confirmant, vous vous apprêtez à anonymiser la fiche de gestion "
            "sociale de cet utilisateur. "
            "Les informations suivantes sont supprimées de façon irréversible </p>"
            "<ul>{}</ul>"
            "<p>Les autres informations sont conservées</p>"
        ).format(fields),
        "validate_button": POSTButton(
            request.current_route_path(),
            "Valider",
            title="Valider la suppression des données utilisateurs",
            icon="check",
            css="btn success",
        ),
        "cancel_button": Link(
            request.route_path(USER_USERDATAS_URL, id=context.id),
            "Annuler",
            title="Annuler la suppression des données utilisateurs",
            icon="times",
            css="btn negative",
        ),
    }


class UserDatasDocTypeView(BaseFormView):
    _schema = None
    title = "Liste des documents fournis par l'entrepreneur"
    form_options = (("formid", "doctypes-form"),)
    add_template_vars = ("current_userdatas", "is_void")

    def __init__(self, *args, **kwargs):
        BaseFormView.__init__(self, *args, **kwargs)
        ensure_doctypes_rel(self.current_userdatas.id, self.request)

    @property
    def current_userdatas(self):
        return self.context

    @property
    def schema(self):
        if self._schema is None:
            self._schema = get_doctypes_schema(self.current_userdatas)

        return self._schema

    @schema.setter
    def schema(self, schema):
        self._schema = schema

    def before(self, form):
        appstruct = {}
        for index, entry in enumerate(self.current_userdatas.doctypes_registrations):
            appstruct["node_%s" % index] = {
                "userdatas_id": entry.userdatas_id,
                "doctype_id": entry.doctype_id,
                "status": entry.status,
            }
        form.set_appstruct(appstruct)
        return form

    @property
    def is_void(self):
        return not self.schema.children

    def submit_success(self, appstruct):
        node_schema = self.schema.children[0]
        for key, value in list(appstruct.items()):
            logger.debug(value)
            model = node_schema.objectify(value)
            self.dbsession.merge(model)

        self.request.session.flash("Vos modifications ont été enregistrées")

        return HTTPFound(self.request.current_route_path())


class UserUserDatasDocTypeView(UserDatasDocTypeView):
    @property
    def current_userdatas(self):
        return self.context.userdatas


def add_views(config):
    """
    Add module related views
    """
    config.add_view(
        userdatas_add_entry_point,
        route_name=USERDATAS_ADD_URL,
        permission=PERMISSIONS["global.create_user"],
    )
    config.add_view(
        userdatas_add_view,
        route_name=USER_USERDATAS_ADD_URL,
        # request_method="POST",
        # require_csrf=True,
        context=User,
        permission=PERMISSIONS["global.view_userdata"],
    )
    config.add_view(
        UserUserDatasEditView,
        route_name=USER_USERDATAS_URL,
        renderer="/userdatas/edit.mako",
        layout="user",
        context=User,
        permission=PERMISSIONS["global.view_userdata"],
    )
    config.add_view(
        UserUserDatasDeleteView,
        route_name=USER_USERDATAS_URL,
        request_param="action=delete",
        require_csrf=True,
        request_method="POST",
        context=User,
        permission=PERMISSIONS["global.view_userdata_details"],
    )
    config.add_view(
        userdata_anonymize_view,
        route_name=USER_USERDATAS_URL,
        request_param="action=anonymize",
        renderer="/base/confirmation.mako",
        request_method="GET",
        context=User,
        permission=PERMISSIONS["global.view_userdata_details"],
    )
    config.add_view(
        userdata_anonymize_view,
        route_name=USER_USERDATAS_URL,
        request_param="action=anonymize",
        require_csrf=True,
        request_method="POST",
        context=User,
        permission=PERMISSIONS["global.view_userdata_details"],
    )
    config.add_view(
        UserUserDatasDocTypeView,
        route_name=USER_USERDATAS_DOCTYPES_URL,
        renderer="/userdatas/doctypes.mako",
        layout="user",
        context=User,
        permission=PERMISSIONS["global.view_userdata_files"],
    )


USERDATAS_MENU = AttrMenuDropdown(
    name="userdatas",
    label="Gestion sociale",
    default_route=USER_USERDATAS_URL,
    icon="address-card",
    hidden_attribute="userdatas",
    perm=[PERMISSIONS["global.view_userdata"]],
)
USERDATAS_MENU.add_item(
    name="userdatas_view",
    label="Fiche du porteur",
    route_name=USER_USERDATAS_URL,
    icon="user-circle",
    perm=[PERMISSIONS["global.view_userdata"]],
)
USERDATAS_MENU.add_item(
    name="userdatas_parcours",
    label="Parcours",
    route_name=USER_USERDATAS_CAREER_PATH_URL,
    other_route_name="career_path",
    icon="chart-line",
    perm=[PERMISSIONS["global.view_userdata"]],
)
USERDATAS_MENU.add_item(
    name="userdatas_doctypes",
    label="Documents sociaux",
    route_name=USER_USERDATAS_DOCTYPES_URL,
    icon="check-square",
    perm=[PERMISSIONS["global.view_userdata_files"]],
)
USERDATAS_MENU.add_item(
    name="userdatas_py3o",
    label="Génération de documents",
    route_name=USER_USERDATAS_PY3O_URL,
    icon="file-alt",
    perm=[PERMISSIONS["global.py3o_userdata"]],
)


def register_menus():
    from caerp.views.user.layout import UserMenu

    UserMenu.add_after("companies", USERDATAS_MENU)


def includeme(config):
    """
    Pyramid main entry point

    :param obj config: The current application config object
    """
    add_views(config)
    register_menus()

import logging
import os

from caerp.consts.permissions import PERMISSIONS
from pyramid.httpexceptions import HTTPFound
from caerp.models import files
from caerp.forms.files import get_template_upload_schema
from caerp.utils.widgets import (
    Link,
    POSTButton,
)
from caerp.utils.datetimes import format_date
from caerp.views import TreeMixin
from caerp.views.files.views import (
    FileUploadView,
    FileEditView,
    file_dl_view,
)
from caerp.views.admin.tools import (
    AdminCrudListView,
    BaseAdminDisableView,
    BaseAdminDeleteView,
)
from caerp.views.admin.userdatas import (
    USERDATAS_URL,
    UserDatasIndexView,
)


log = logging.getLogger(__name__)


UPLOAD_OK_MSG = "Le modèle de document a bien été ajouté"
EDIT_OK_MSG = "Le modèle de document a bien été modifié"


TEMPLATE_URL = os.path.join(USERDATAS_URL, "templates")
TEMPLATE_ITEM_URL = os.path.join(TEMPLATE_URL, "{id}")


class TemplateListView(AdminCrudListView):
    """
    Listview of templates
    """

    title = "Modèles de documents"
    route_name = TEMPLATE_URL
    item_route_name = TEMPLATE_ITEM_URL
    columns = ("Nom du fichier", "Description", "Déposé le")
    permission = PERMISSIONS["global.config_userdatas"]

    def stream_actions(self, item):
        yield Link(
            self._get_item_url(item),
            "Télécharger",
            title="Télécharger le fichier odt",
            icon="download",
            css="icon",
        )
        yield Link(
            self._get_item_url(item, action="edit"),
            "Modifier",
            title="Modifier le modèle",
            icon="pen",
            css="icon",
        )
        if item.active:
            yield POSTButton(
                self._get_item_url(item, action="disable"),
                "Désactiver",
                title="Désactiver le modèle afin qu'il ne soit plus proposé",
                icon="lock",
                css="icon",
            )
        else:
            yield POSTButton(
                self._get_item_url(item, action="disable"),
                "Activer",
                title="Activer le modèle afin qu'il soit proposé dans " "l'interface",
                icon="lock-open",
                css="icon",
            )
            yield POSTButton(
                self._get_item_url(item, action="delete"),
                "Supprimer",
                title="Supprimer définitivement le modèle",
                confirm="Êtes-vous sûr de vouloir supprimer ce modèle ?",
                icon="trash-alt",
                css="icon negative",
            )

    def stream_columns(self, item):
        yield item.name
        yield item.description
        yield format_date(item.updated_at)

    def more_template_vars(self, result):
        result[
            "help_msg"
        ] = "Les modèles de document doivent être au format \
odt pour pouvoir être utilisés par enDI"
        result["column_width"] = "width80"
        return result

    def load_items(self):
        templates = files.Template.query().order_by(
            files.Template.active.desc(), files.Template.name.asc()
        )
        return templates


class TemplateAddView(FileUploadView, TreeMixin):
    title = "Ajouter un modèle de documents"
    route_name = TEMPLATE_URL
    factory = files.Template
    valid_msg = UPLOAD_OK_MSG
    add_template_vars = ("title", "breadcrumb", "back_link")
    permission = PERMISSIONS["global.config_userdatas"]

    def __init__(self, context, request=None):
        super().__init__(context, request)
        self.controller.factory = files.Template

    def get_schema(self):
        return get_template_upload_schema()

    def redirect(self, come_from=None):
        if come_from:
            return FileUploadView.redirect(self, come_from)
        else:
            return HTTPFound(".")

    def __call__(self):
        self.populate_navigation()
        return FileUploadView.__call__(self)


class TemplateEditView(FileEditView, TreeMixin):
    route_name = TEMPLATE_ITEM_URL
    valid_msg = "Le modèle de document a bien été modifié"
    factory = files.Template
    valid_msg = EDIT_OK_MSG
    add_template_vars = ("title", "breadcrumb", "back_link")
    permission = PERMISSIONS["global.config_userdatas"]

    def __init__(self, context, request=None):
        super().__init__(context, request)
        self.controller.factory = files.Template

    def __call__(self):
        self.populate_navigation()
        return FileEditView.__call__(self)

    def get_schema(self):
        return get_template_upload_schema()

    def redirect(self, come_from=None):
        if come_from:
            return FileUploadView.redirect(self, come_from)
        else:
            return HTTPFound(TEMPLATE_URL)


class TemplateDisableView(BaseAdminDisableView):
    route_name = TEMPLATE_ITEM_URL
    enable_msg = "Le template a bien été activé"
    disable_msg = "Le template a bien été désactivé"
    permission = PERMISSIONS["global.config_userdatas"]


class TemplateDeleteView(BaseAdminDeleteView):
    route_name = TEMPLATE_ITEM_URL
    delete_msg = "Le modèle a bien été supprimé"
    permission = PERMISSIONS["global.config_userdatas"]


def includeme(config):
    config.add_route(TEMPLATE_URL, TEMPLATE_URL)
    config.add_route(TEMPLATE_ITEM_URL, TEMPLATE_ITEM_URL, traverse="templates/{id}")

    config.add_admin_view(
        TemplateListView,
        parent=UserDatasIndexView,
        renderer="caerp:templates/admin/crud_list.mako",
    )
    config.add_admin_view(
        TemplateAddView,
        parent=TemplateListView,
        request_param="action=add",
    )
    config.add_admin_view(
        file_dl_view,
        route_name=TEMPLATE_ITEM_URL,
    )
    config.add_admin_view(
        TemplateEditView,
        parent=TemplateListView,
        request_param="action=edit",
    )
    config.add_admin_view(
        TemplateDisableView,
        parent=TemplateListView,
        request_param="action=disable",
        require_csrf=True,
        request_method="POST",
    )
    config.add_admin_view(
        TemplateDeleteView,
        parent=TemplateListView,
        request_param="action=delete",
        require_csrf=True,
        request_method="POST",
    )

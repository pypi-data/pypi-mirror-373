import logging
import os

from caerp.consts.permissions import PERMISSIONS
from caerp.views.admin.tools import AdminCrudListView, BaseAdminEditView
from caerp.forms.admin.sale.form_options import (
    get_admin_form_field_definition_schema,
)
from caerp.models.form_options import FormFieldDefinition

from caerp.utils.widgets import Link

from . import FORMS_URL, FormsIndexView

FIELD_COLLECTION_URL = os.path.join(FORMS_URL, "form_field_definitions")
FIELD_ITEM_URL = os.path.join(FIELD_COLLECTION_URL, "{id}")


logger = logging.getLogger(__name__)


class FormFieldDefinitionAdminView(AdminCrudListView):
    title = "Personnalisation des champs du formulaire"
    description = (
        "Activer/Désactiver/Personnaliser l'utilisation de certains "
        "champs de formulaire"
    )
    columns = ["Formulaire", "Champ", "Statut"]
    route_name = FIELD_COLLECTION_URL
    item_route_name = FIELD_ITEM_URL
    factory = FormFieldDefinition

    permission = PERMISSIONS["global.config_sale"]

    def get_addurl(self):
        return None

    def stream_columns(self, item):
        if item.form == "task":
            yield "Devis/Facture"
        else:
            yield "Inconnu"

        yield "{} ({})".format(item.title, item.field_name)

        if not item.visible:
            yield "{} Pas utilisé".format(self.get_icon("eye-slash"))
        elif item.required:
            yield "{} Obligatoire".format(self.get_icon("required"))
        else:
            yield "Facultatif"

    def stream_actions(self, item):
        yield Link(self._get_item_url(item), "Voir/Modifier", icon="pen", css="icon")

    def load_items(self):
        return (
            self.request.dbsession.query(self.factory)
            .order_by(self.factory.form)
            .order_by(self.factory.field_name)
        )


class FormFieldEditView(BaseAdminEditView):
    route_name = FIELD_ITEM_URL
    factory = FormFieldDefinition
    schema = get_admin_form_field_definition_schema()
    named_form_grid = (
        (("visible", 12),),
        (("title", 12),),
        (("required", 12),),
    )

    @property
    def help_msg(self):
        if self.context.form == "task":
            form_label = "Devis/Facture"
        else:
            form_label = "Inconnu"
        return "Configurez le champ {} du formulaire {} ".format(
            self.context.field_name, form_label
        )

    @property
    def title(self):
        return "Modifier la configuration du champ '{}'".format(self.context.title)


def includeme(config):
    config.add_route(FIELD_COLLECTION_URL, FIELD_COLLECTION_URL)
    config.add_route(
        FIELD_ITEM_URL,
        FIELD_ITEM_URL,
        traverse="/form_field_definitions/{id}",
    )
    config.add_admin_view(
        FormFieldDefinitionAdminView,
        parent=FormsIndexView,
        renderer="admin/crud_list.mako",
    )
    config.add_admin_view(
        FormFieldEditView,
        parent=FormFieldDefinitionAdminView,
        renderer="admin/crud_add_edit.mako",
    )

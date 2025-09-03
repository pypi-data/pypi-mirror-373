import os
import logging
import colander
import json

from caerp.consts.permissions import PERMISSIONS
from deform_extensions import AccordionFormWidget
from pyramid.httpexceptions import HTTPFound

from caerp.models.config import Config
from caerp.models.user.userdatas import UserDatasCustomFields
from caerp.utils.colanderalchemy import (
    get_colanderalchemy_column_info,
    get_colanderalchemy_model_sections,
    get_model_columns_by_colanderalchemy_section,
)
from caerp.views.admin.tools import BaseAdminFormView
from caerp.views.admin.userdatas import (
    USERDATAS_URL,
    UserDatasIndexView,
)

logger = logging.getLogger(__name__)

CUSTOM_FIELDS_URL = os.path.join(USERDATAS_URL, "custom_fields")


class CustomFieldsView(BaseAdminFormView):
    title = "Champs complémentaires"
    description = ""
    route_name = CUSTOM_FIELDS_URL
    schema = None
    schema_grid = {}
    validation_msg = "Champs complémentaires mis à jour avec succès"

    permission = PERMISSIONS["global.config_userdatas"]

    def __init__(self, context, request=None):
        super().__init__(context, request)
        title = "Configurer l'affichage des champs complémentaires"
        schema = colander.Schema(title=title)
        schema_grid = {}
        sections_list = get_colanderalchemy_model_sections(UserDatasCustomFields)
        sections_list.insert(0, None)  # To get fields with no section
        for section in sections_list:
            section_grid = ()
            for field in get_model_columns_by_colanderalchemy_section(
                UserDatasCustomFields, section
            ):
                section_grid += (((field.name, 12),),)
                schema.add(
                    colander.SchemaNode(
                        colander.Boolean(),
                        name=field.name,
                        title=get_colanderalchemy_column_info(field, "title"),
                        section=get_colanderalchemy_column_info(field, "section"),
                    ),
                )
            schema_grid[section] = section_grid
        self.schema = schema
        self.schema_grid = schema_grid

    def before(self, form):
        appstruct = {}
        custom_fields_to_display = json.loads(
            Config.get_value("userdatas_active_custom_fields", "[]")
        )
        for field in custom_fields_to_display:
            appstruct[field] = True
        form.set_appstruct(appstruct)
        form.widget = AccordionFormWidget(named_grids=self.schema_grid)

    def submit_success(self, appstruct):
        custom_fields_to_display = []
        for field in appstruct:
            if appstruct[field]:
                custom_fields_to_display.append(field)
        Config.set(
            "userdatas_active_custom_fields", json.dumps(custom_fields_to_display)
        )

        self.request.session.flash(self.validation_msg)
        back_link = self.back_link
        result = None
        if back_link is not None:
            result = HTTPFound(back_link)
        return result


def includeme(config):
    config.add_route(CUSTOM_FIELDS_URL, CUSTOM_FIELDS_URL)
    config.add_admin_view(
        CustomFieldsView,
        parent=UserDatasIndexView,
    )

import colander
import deform
from colanderalchemy import SQLAlchemySchemaNode
from caerp.models.form_options import FormFieldDefinition
from caerp.forms import customize_field


def get_admin_form_field_definition_schema():
    excludes = (
        "id",
        "field_name",
        "form",
        "default",
    )

    schema = SQLAlchemySchemaNode(FormFieldDefinition, excludes=excludes)
    customize_field(
        schema,
        "required",
    )
    return schema

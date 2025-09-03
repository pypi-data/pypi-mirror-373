import deform
from colanderalchemy import SQLAlchemySchemaNode

from caerp.models.task.mentions import TaskMention

from caerp.forms import (
    customize_field,
)

from caerp.forms import richtext_widget


def get_admin_task_mention_schema():
    """
    Build the task mentions admin schema
    """
    schema = SQLAlchemySchemaNode(
        TaskMention,
        includes=(
            "label",
            "help_text",
            "title",
            "full_text",
            "order",
        ),
    )
    customize_field(
        schema,
        "label",
        title="Libellé",
        description="Libellé utilisé dans l'interface",
    )
    customize_field(
        schema,
        "full_text",
        widget=richtext_widget(admin=True),
    )
    customize_field(schema, "order", widget=deform.widget.HiddenWidget())
    return schema

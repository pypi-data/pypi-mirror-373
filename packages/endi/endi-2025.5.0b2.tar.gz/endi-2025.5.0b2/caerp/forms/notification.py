import colander
import colanderalchemy
from caerp.models.notification import Notification
from caerp.forms.lists import BaseListsSchema


def get_list_schema() -> colander._SchemaNode:
    """
    Return the schema for the job list search form
    """
    schema: colander._SchemaNode = BaseListsSchema().clone()
    del schema["search"]
    schema.add(
        colander.SchemaNode(
            colander.DateTime(),
            name="filter_due_date",
            title="Échéance",
            missing=colander.drop,
        ),
    )
    schema.add(
        colander.SchemaNode(
            colander.String(),
            name="filter_key",
            title="Type de notification",
            missing=colander.drop,
        ),
    )
    schema.add(
        colander.SchemaNode(
            colander.String(),
            name="filter_channel",
            title="Channel de la notification",
            missing="message",
        ),
    )

    return schema


def get_edit_schema() -> colanderalchemy.SQLAlchemySchemaNode:
    """Build the notification edition schema

    :return: _description_
    :rtype: colanderalchemy.SQLAlchemySchemaNode
    """
    return colanderalchemy.SQLAlchemySchemaNode(
        Notification,
        includes=("due_date", "read"),
    )

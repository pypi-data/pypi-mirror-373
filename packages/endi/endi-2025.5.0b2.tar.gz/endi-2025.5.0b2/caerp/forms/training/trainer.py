import functools
import deform

from colanderalchemy import SQLAlchemySchemaNode
from caerp import forms
from caerp.forms.user.user import get_list_schema as get_user_list_schema
from caerp.models.training.trainer import TrainerDatas


FORM_GRID = {
    "Profil Professionnel": (
        (("specialty", 12),),
        (("linkedin", 6), ("viadeo", 6)),
        (("career", 12),),
        (("qualifications", 12),),
        (("background", 12),),
        (("references", 12),),
    ),
    "Concernant votre activité de formation": (
        (("motivation", 12),),
        (("approach", 12),),
    ),
}


def customize_schema(schema):
    """
    Customize the given TrainerDatas schema to setup specific widgets ...
    """
    customize = functools.partial(forms.customize_field, schema)
    for field in (
        "specialty",
        "career",
        "qualifications",
        "references",
        "motivation",
        "approach",
    ):
        customize(field, widget=deform.widget.TextAreaWidget())
    return schema


def get_add_edit_trainerdatas_schema():
    """
    Build the form schemas for adding/modifying a TrainerDatas entry

    :returns: a colanderalchemy.SQLAlchemySchemaNode
    """
    schema = SQLAlchemySchemaNode(
        TrainerDatas, excludes=("name", "_acl", "user_id", "active")
    )
    customize_schema(schema)
    return schema


def get_list_schema():
    """
    Build the form schema for trainers listing

    :returns: a colanderalchemy.SQLAlchemySchemaNode
    """
    schema = get_user_list_schema()
    return schema

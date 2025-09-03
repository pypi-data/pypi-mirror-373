import colander

from colanderalchemy import SQLAlchemySchemaNode
from caerp.models.statistics import (
    StatisticCriterion,
    StatisticEntry,
    StatisticSheet,
)
from caerp.statistics import STATISTIC_FILTER_OPTIONS
from caerp.forms import get_deferred_select_validator


def get_defererd_uniq_validator(model, attribute):
    """
    Build a unique attribute value validator

    :param cls model: The SQLAlchemy model
    :param str attribute: The attribute expected to be unique
    """

    @colander.deferred
    def deferred_validator(node, kw):
        request = kw["request"]
        query = request.dbsession.query(getattr(model, "id"))
        if isinstance(request.context, model):
            query = query.filter(getattr(model, "id") != request.context.id)

        def validator(value):
            nonlocal query
            query = query.filter(getattr(model, attribute) == value)
            if query.count() > 0:
                return "Ce nom est déjà utilisé"
            return True

        return colander.Function(validator)

    return deferred_validator


def get_sheet_add_edit_schema():
    schema = SQLAlchemySchemaNode(StatisticSheet, includes=("title",))
    schema["title"].missing = colander.required
    schema["title"].validator = get_defererd_uniq_validator(StatisticSheet, "title")
    return schema


def get_entry_add_edit_schema():
    schema = SQLAlchemySchemaNode(
        StatisticEntry,
        includes=(
            "title",
            "description",
        ),
    )
    schema["title"].missing = colander.required
    return schema


def is_list(value):
    return isinstance(value, (list, tuple))


def customize_criterion_schema(criterion_type, schema, edit=False):
    if "entry_id" in schema:
        schema["entry_id"].validator = get_deferred_select_validator(StatisticEntry)
    if "method" in schema:
        schema["method"].validator = colander.OneOf(
            [a["value"] for a in STATISTIC_FILTER_OPTIONS[criterion_type]]
        )

    if "searches" in schema:
        schema["searches"].typ = colander.List()
        schema["searches"].validator = colander.Function(
            is_list, msg="Doit être une liste"
        )

    if edit and "type" in schema:
        if criterion_type == "or":
            schema["type"].validator = colander.OneOf(("and", "or"))
        elif criterion_type == "onetomany":
            schema["type"].validator = colander.OneOf(("onetomany",))
        else:
            schema["type"].validator = colander.OneOf(
                (
                    "string",
                    "number",
                    "date",
                    "multidate",
                    "bool",
                    "static_opt",
                    "manytoone",
                )
            )
    return schema


def get_criterion_add_edit_schema(criterion_type, edit=False):
    """
    Returns add / edit schema for Stat criterion
    """
    if criterion_type in ("or", "and"):
        includes = ("type", "entry_id", "parent_id")

    elif criterion_type == "onetomany":
        includes = ("type", "key", "entry_id", "parent_id")

    elif criterion_type in ("multidate", "date"):
        includes = (
            "type",
            "key",
            "method",
            "date_search1",
            "date_search2",
            "entry_id",
            "parent_id",
        )
    elif criterion_type in ("string", "number"):
        includes = (
            "type",
            "key",
            "method",
            "search1",
            "search2",
            "entry_id",
            "parent_id",
        )
    elif criterion_type in ("static_opt", "manytoone"):
        includes = ("type", "key", "method", "searches", "entry_id", "parent_id")
    elif criterion_type == "bool":
        includes = ("type", "key", "method", "entry_id", "parent_id")

    schema = SQLAlchemySchemaNode(StatisticCriterion, includes)
    customize_criterion_schema(criterion_type, schema, edit=edit)
    return schema

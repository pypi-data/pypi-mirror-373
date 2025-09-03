"""
    Career path forms configuration
"""
import colander
import functools
from colanderalchemy import SQLAlchemySchemaNode
from caerp.forms import (
    customize_field,
    get_deferred_select,
    get_select,
)
from caerp.models.career_stage import CareerStage
from caerp.models.career_path import (
    CareerPath,
    PERIOD_OPTIONS,
    TypeContratOption,
    EmployeeQualityOption,
    TypeSortieOption,
    MotifSortieOption,
)


def end_date_validator(node, appstruct):
    """
    Check if end_date is posterior to start_date
    :param node:
    :param appstruct:
    :return: Exception exc
    """
    end_date = appstruct["end_date"]
    start_date = appstruct["start_date"]
    if end_date not in (None, colander.null) and start_date not in (
        None,
        colander.null,
    ):
        if appstruct["start_date"] > appstruct["end_date"]:
            exc = colander.Invalid(
                node,
                "La date d'échéance doit être postérieure à la date d'effet",
            )
            exc["end_date"] = "Doit être postérieure à la date d'effet"
            raise exc


def customize_schema(schema):
    """
    Customize the form schema
    :param obj schema: A CareerPath schema
    """
    customize = functools.partial(customize_field, schema)
    customize(
        "career_stage_id",
        get_deferred_select(CareerStage, keys=("id", "name")),
        missing=colander.required,
    )
    customize("type_contrat_id", get_deferred_select(TypeContratOption))
    customize("employee_quality_id", get_deferred_select(EmployeeQualityOption))
    customize("goals_period", get_select(PERIOD_OPTIONS))
    customize("type_sortie_id", get_deferred_select(TypeSortieOption))
    customize("motif_sortie_id", get_deferred_select(MotifSortieOption))
    schema.validator = end_date_validator


def get_add_stage_schema():
    """
    Return a schema for adding a new career path's stage
    Only display stage's type and dates
    """
    schema = SQLAlchemySchemaNode(
        CareerPath,
        (
            "start_date",
            "end_date",
            "career_stage_id",
        ),
    )
    customize_schema(schema)
    return schema


def get_edit_stage_schema(stage_type):
    """
    Return a schema for editing career path's stage
    related to the stage's type
    """
    fields = [
        "id",
        "start_date",
        "end_date",
    ]

    if stage_type == "contract":
        fields.extend(
            [
                "type_contrat_id",
                "employee_quality_id",
                "taux_horaire",
                "hourly_rate_string",
                "num_hours",
                "parcours_salary",
                "goals_amount",
                "goals_period",
            ]
        )

    elif stage_type == "amendment":
        fields.extend(
            [
                "type_contrat_id",
                "employee_quality_id",
                "taux_horaire",
                "hourly_rate_string",
                "num_hours",
                "parcours_salary",
                "goals_amount",
                "goals_period",
                "amendment_number",
            ]
        )
    elif stage_type == "exit":
        fields.extend(
            [
                "type_sortie_id",
                "motif_sortie_id",
            ]
        )
    schema = SQLAlchemySchemaNode(CareerPath, fields)
    customize_schema(schema)
    return schema

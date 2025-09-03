import colander
import deform
import deform_extensions
from colanderalchemy import SQLAlchemySchemaNode

from sqlalchemy import not_

from caerp import forms
from caerp.models.project.types import (
    ProjectType,
    BusinessType,
)
from caerp.forms import (
    customize_field,
    get_deferred_model_select,
    get_sequence_child_item,
    get_deferred_model_select_checkbox,
)


def _build_unique_label_validator(class_, type_id=None):
    """
    Return a unique label validator

    :param int type_id: Exception id
    :returns: A validator
    :rtype: function
    """

    def validator(node, value):
        if not class_.unique_label(value, type_id):
            message = "Ce nom n'est pas disponible : {0}".format(value)
            raise colander.Invalid(node, message)

    return validator


def validate_at_least_one_compute_mode(node, value):
    mode_keys = ["ttc_compute_mode_allowed", "ht_compute_mode_allowed"]

    if not True in [value[k] for k in mode_keys]:
        msg = "Au moins un mode de saisie des prix doit etre activé."
        exc = colander.Invalid(node, msg)
        for k in mode_keys:
            exc[k] = msg
        raise exc


def get_deferred_unique_label_validator(class_):
    """
    Returns a unique label validator for the given class

    :param obj class_: The classname ProjectType/BusinessType
    """

    @colander.deferred
    def deferred_unique_label_validator(node, kw):
        """
        Deferred unique validator
        """
        context = kw["request"].context
        if isinstance(context, (ProjectType, BusinessType)):
            type_id = context.id
        else:
            type_id = None
        return _build_unique_label_validator(class_, type_id=type_id)

    return deferred_unique_label_validator


def remove_attrs_on_private_context(schema, kw):
    context = kw["request"].context
    if isinstance(context, ProjectType):
        if not context.editable:
            del schema["label"]
            del schema["with_business"]


def get_admin_project_type_schema():
    schema = SQLAlchemySchemaNode(
        ProjectType,
        includes=(
            "label",
            "ht_compute_mode_allowed",
            "ttc_compute_mode_allowed",
            "include_price_study",
            "price_study_mode",
            "with_business",
            "other_business_types",
        ),
        validator=validate_at_least_one_compute_mode,
    )
    customize_field(
        schema,
        "label",
        validator=get_deferred_unique_label_validator(ProjectType),
    )
    customize_field(
        schema,
        "include_price_study",
        widget=deform_extensions.CheckboxToggleWidget(
            true_target="price_study_mode",
        ),
    )
    customize_field(
        schema,
        "price_study_mode",
        widget=deform.widget.RadioChoiceWidget(
            values=(
                ("optionnal", "Saisie Classique par défaut"),
                ("default", "Étude de prix par défaut"),
                ("mandatory", "Étude de prix obligatoire"),
            )
        ),
    )
    schema.add_before(
        "other_business_types",
        forms.CustomModelSchemaNode(
            colander.Integer(),
            name="default_business_type",
            remote_name="id",
            model=BusinessType,
            title="Type d'affaire par défaut pour ce type de dossier",
            widget=get_deferred_model_select(
                BusinessType,
                filters=[["active", True]],
            ),
        ),
    )
    customize_field(
        schema,
        "other_business_types",
        title="Autres types d'affaire disponibles pour ce type de dossier",
        children=get_sequence_child_item(BusinessType),
        widget=get_deferred_model_select_checkbox(
            BusinessType,
            filters=[["active", True]],
        ),
    )
    schema.after_bind = remove_attrs_on_private_context
    return schema


@colander.deferred
def get_deferred_unique_project_type_default(node, kw):
    """
    Ensure a business type is not a default for a project type already having
    a default value
    """
    context = kw["request"].context

    def validator(node, value):
        query = (
            BusinessType.query().filter_by(project_type_id=value).filter_by(active=True)
        )
        if isinstance(context, BusinessType):
            query = query.filter(not_(BusinessType.id == context.id))

        if query.count() > 0:
            raise colander.Invalid(
                node, "Ce type de dossier a déjà un type d'affaire par défaut"
            )

    return validator


def remove_attrs_on_private_business_type(schema, kw):
    context = kw["request"].context
    if isinstance(context, BusinessType):
        if not context.editable:
            del schema["label"]
            del schema["bpf_related"]
            del schema["tva_on_margin"]


def get_admin_business_type_schema(edit=False):
    schema = SQLAlchemySchemaNode(
        BusinessType,
        includes=(
            "label",
            "project_type_id",
            "other_project_types",
            "bpf_related",
            "tva_on_margin",
            "coop_cgv_override",
        ),
    )

    customize_field(
        schema,
        "label",
        validator=get_deferred_unique_label_validator(BusinessType),
    )
    customize_field(
        schema,
        "project_type_id",
        widget=get_deferred_model_select(ProjectType),
        validator=get_deferred_unique_project_type_default,
    )
    customize_field(
        schema,
        "other_project_types",
        children=get_sequence_child_item(ProjectType),
        widget=get_deferred_model_select_checkbox(
            ProjectType,
            filters=[["active", True]],
        ),
    )
    customize_field(
        schema,
        "coop_cgv_override",
        widget=forms.richtext_widget(),
    )
    schema.after_bind = remove_attrs_on_private_context
    return schema

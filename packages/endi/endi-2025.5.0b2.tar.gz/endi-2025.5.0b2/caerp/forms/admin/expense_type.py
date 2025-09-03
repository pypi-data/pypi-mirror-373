import functools
import colander
import deform

from colanderalchemy import SQLAlchemySchemaNode

from caerp import forms
from caerp.models.expense.types import (
    ExpenseType,
    ExpenseKmType,
    ExpenseTelType,
)


def validate_tva_on_margin_fields(node, cstruct):
    tva_on_margin = cstruct["tva_on_margin"]
    compte_produit_tva_on_margin = cstruct["compte_produit_tva_on_margin"]

    if tva_on_margin and not compte_produit_tva_on_margin:
        raise colander.Invalid(
            node,
            "Un compte produit pour la TVA sur marge doit être rempli",
        )
    if not tva_on_margin and compte_produit_tva_on_margin:
        raise colander.Invalid(
            node,
            "Un compte produit pour la TVA sur marge ne peut pas être "
            "renseigné si le mode TVA sur marge n'est pas activé.",
        )

    is_internal = cstruct["internal"]
    if tva_on_margin and is_internal:
        raise colander.Invalid(
            node,
            "Vous ne pouvez activer la TVA sur marge pour les dépenses "
            "spécifiques à la sous-traitance interne",
        )


def convert_zero_to_None(cstruct):
    if cstruct in (0, "0"):
        cstruct = None
    return cstruct


def _customize_expense_type_fields(schema):
    """
    Customize schema to add ui related stuff

    :param obj schema: a colander.Schema
    """
    customize = functools.partial(forms.customize_field, schema)
    if "label" in schema:
        customize("label", missing=colander.required)
    if "category" in schema:
        customize(
            "category",
            widget=deform.widget.RadioChoiceWidget(
                values=(
                    (ExpenseType.EXPENSE_CATEGORY, "Frais"),
                    (
                        ExpenseType.PURCHASE_CATEGORY,
                        "Achat",
                    ),
                    # 0 devient None grâce au preparer ci-dessous
                    # Mais ici colander requiert une String
                    ("0", "Les deux"),
                )
            ),
            default="0",
            missing=None,
            preparer=convert_zero_to_None,
            validator=colander.OneOf(["1", "2", None]),
        )
    return schema


def get_expense_type_schema(factory=ExpenseType, excludes=None, includes=None):
    """
    Build a form schema for ExpenseType administration
    """
    if includes is not None:
        excludes = None
    else:
        excludes = ("type", "active", "id")

    schema = SQLAlchemySchemaNode(
        factory,
        includes=includes,
        excludes=excludes,
    )
    if "tva_on_margin" in schema:
        schema.validator = validate_tva_on_margin_fields

    schema = _customize_expense_type_fields(schema)
    return schema


def get_expense_kmtype_schema(excludes=None, includes=None):
    """
    Build a form schema for ExpenseKmType administration
    """
    return get_expense_type_schema(factory=ExpenseKmType)


def get_expense_teltype_schema(excludes=None, includes=None):
    """
    Build a form schema for ExpenseTelType administration
    """
    schema = get_expense_type_schema(factory=ExpenseTelType)
    customize = functools.partial(forms.customize_field, schema)
    customize("percentage", missing=colander.required)
    return schema

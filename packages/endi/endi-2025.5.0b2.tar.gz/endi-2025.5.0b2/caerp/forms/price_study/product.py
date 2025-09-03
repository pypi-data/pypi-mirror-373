import functools
import colander
from colanderalchemy import SQLAlchemySchemaNode

from caerp.utils.html import clean_html

from caerp.models.tva import (
    Tva,
    Product,
)
from caerp.models.task import WorkUnit
from caerp.models.price_study.work import PriceStudyWork
from caerp.models.price_study.product import PriceStudyProduct

from caerp import forms
from caerp.forms.custom_types import (
    AmountType,
    QuantityType,
)
from caerp.forms.company import get_deferred_company_attr_default

from .common import (
    deferred_default_product_id,
    deferred_default_tva_id,
)


def customize_product_schema(schema, edit=True):
    """
    Customize the fields to set custom default/missing/validators

    :param obj schema: A SQLAlchemySchemaNode instance
    :returns: The modified schema
    """
    customize = functools.partial(forms.customize_field, schema)

    if "description" in schema:
        customize("description", preparer=clean_html)

    if "supplier_ht" in schema:
        customize("supplier_ht", typ=AmountType(5), missing=None)

    if "ht" in schema:
        customize("ht", typ=AmountType(5), missing=None)

    if "unity" in schema:
        customize(
            "unity",
            validator=forms.get_deferred_select_validator(WorkUnit, id_key="label"),
            missing=None,
        )

    if "tva_id" in schema:
        customize(
            "tva_id",
            validator=forms.get_deferred_select_validator(Tva),
            missing=colander.required,
        )
    if "product_id" in schema:
        customize(
            "product_id",
            validator=forms.get_deferred_select_validator(Product),
            missing=colander.required,
        )
    if "margin_rate" in schema:
        customize("margin_rate", typ=QuantityType(), missing=None)
        if not edit:
            customize(
                "margin_rate", missing=get_deferred_company_attr_default("margin_rate")
            )

    if "total_ht" in schema:
        customize("total_ht", typ=AmountType(5), missing=None)

    if "quantity" in schema:
        customize("quantity", typ=QuantityType())


PRODUCT_EXCLUDES = (
    "id",
    "chapter_id",
    "type_",
    "chapter",
    "tva",
    "product",
    "base_sale_product",
    "sale_product_work",
    "items",
    "task_line_id",
    "task_line",
    "price_study",
)
# Valeurs calculées
WORK_EXCLUDES = PRODUCT_EXCLUDES + (
    "ht",
    "total_ht",
)


def get_product_edit_schema(factory, excludes=(), edit=True):
    """
    Build a PriceStudyProduct edit schema regarding the given factory

    :param class factory: A model class
    """
    if factory == PriceStudyWork:
        excludes = WORK_EXCLUDES + excludes

    else:
        excludes = PRODUCT_EXCLUDES[:] + excludes

    schema = SQLAlchemySchemaNode(factory, excludes=excludes)
    customize_product_schema(schema, edit=edit)
    return schema


def get_product_add_schema(type_):
    if type_ == "price_study_work":
        factory = PriceStudyWork
    else:
        factory = PriceStudyProduct

    schema = get_product_edit_schema(factory, edit=False)
    return schema

"""
Sale product related form schemas
"""
import colander
import functools
import deform
from colanderalchemy import SQLAlchemySchemaNode

from caerp.models.third_party.supplier import Supplier
from caerp.models.tva import (
    Tva,
    Product,
)
from caerp.models.task import WorkUnit
from caerp.models.sale_product.base import BaseSaleProduct, SaleProductStockOperation
from caerp.models.sale_product.training import (
    SaleProductTraining,
)
from caerp.models.sale_product.work import SaleProductWork
from caerp.models.sale_product.category import SaleProductCategory
from caerp.models.company import Company
from caerp.models.expense.types import ExpenseType

from caerp.utils.html import clean_html
from caerp import forms
from caerp.forms.company import get_deferred_company_attr_default
from caerp.forms.lists import BaseListsSchema
from caerp.forms.custom_types import (
    AmountType,
    QuantityType,
)
from caerp.forms.sale_product.work import customize_work_item_schema


def _deferred_company_id_filter(node, kw):
    """
    Build a SQLAlchemy filter for company_id at execution time
    """
    context = kw["request"].context
    if isinstance(context, BaseSaleProduct):
        return {"company_id": context.company_id}
    elif isinstance(context, Company):
        return {"company_id": context.id}
    else:
        raise Exception(
            "Context is not one of BaseSaleProduct, Company {}".format(context)
        )


@colander.deferred
def deferred_last_sale_product_mode(node, kw):
    """
    Retrieve the last product mode that was used by the current company

    NB : only used in add mode, context is Company
    """
    company = kw["request"].context
    if not isinstance(company, Company):
        return "ht"
    else:
        result = BaseSaleProduct.find_last_used_mode(company.id)
        if not result:
            result = "ht"
    return result


def customize_sale_product_and_sale_product_work_schema(schema, edit=True):
    """
    Customize the sale product schema to add custom validators and defaults

    :param obj schema: The SQLAlchemySchemaNode instance
    """
    customize = functools.partial(forms.customize_field, schema)
    customize("type_", validator=colander.OneOf(BaseSaleProduct.ALL_TYPES))
    if "description" in schema:
        customize(
            "description",
            preparer=clean_html,
        )
    if "ht" in schema:
        customize("ht", typ=AmountType(5), missing=None)

    if "ttc" in schema:
        customize("ttc", typ=AmountType(5), missing=None)

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
            missing=None,
        )
    if "product_id" in schema:
        customize(
            "product_id",
            validator=forms.get_deferred_select_validator(Product),
            missing=None,
        )
    # Seulement les suppliers de la company
    if "supplier_id" in schema:
        customize(
            "supplier_id",
            validator=forms.get_deferred_select_validator(
                Supplier,
                filters=[_deferred_company_id_filter],
            ),
            missing=None,
        )

    if "supplier_ht" in schema:
        customize("supplier_ht", typ=AmountType(5), missing=None)

    if "purchase_type_id" in schema:
        customize(
            "purchase_type_id",
            validator=forms.get_deferred_select_validator(ExpenseType),
        )

    if "category_id" in schema:
        customize(
            "category_id",
            validator=forms.get_deferred_select_validator(
                SaleProductCategory,
                filters=[_deferred_company_id_filter],
            ),
        )

    if "notes" in schema:
        customize(
            "notes",
            preparer=clean_html,
        )

    if "items" in schema:
        customize(
            "items",
            validator=colander.Length(
                min=1, min_err="Un produit au moins doit être inclus"
            ),
        )
        child_schema = schema["items"].children[0]
        customize_work_item_schema(child_schema, from_work_schema=True)

    if "mode" in schema:
        if not edit:
            customize(
                "mode",
                missing=deferred_last_sale_product_mode,
            )

    if "margin_rate" in schema:
        customize("margin_rate", typ=QuantityType(), validator=colander.Range(0, 0.999))

    return schema


BASE_SALE_PRODUCT_EXCLUDES = (
    "id",
    "company_id",
    "company",
    "product",
    "tva",
    "supplier",
    "purchase_type",
    "category",
)


def get_sale_product_add_edit_schema(factory, includes=None, edit=True):
    """
    Build a Sale product add edit schema

    :returns: A colanderalchemy.SQLAlchemySchemaNode schema
    """
    if includes is None:
        excludes = BASE_SALE_PRODUCT_EXCLUDES[:]  # on crée une copie

        if factory in (SaleProductWork, SaleProductTraining):
            excludes += (
                "supplier_id",
                "supplier_unity_amount",
                "purchase_type",
                "supplier_ht",
            )
    else:
        excludes = None

    schema = SQLAlchemySchemaNode(factory, excludes=excludes, includes=includes)

    schema = customize_sale_product_and_sale_product_work_schema(schema, edit)
    return schema


def get_sale_product_list_schema():
    """
    Build a colander schema for sale product listing
    """
    schema = BaseListsSchema().clone()

    schema.add(
        colander.SchemaNode(
            colander.String(),
            name="type_",
            validator=colander.OneOf(BaseSaleProduct.ALL_TYPES),
            missing=colander.drop,
        )
    )
    schema.add(
        colander.SchemaNode(
            colander.String(),
            name="description",
            missing="",
            widget=deform.widget.TextInputWidget(css_class="input-medium search-query"),
            default="",
        )
    )
    schema.add(
        colander.SchemaNode(
            colander.String(),
            name="supplier_ref",
            missing="",
            widget=deform.widget.TextInputWidget(css_class="input-medium search-query"),
            default="",
        )
    )
    schema.add(
        colander.SchemaNode(
            colander.Integer(),
            name="category_id",
            validator=forms.get_deferred_select_validator(
                SaleProductCategory,
                filters=[_deferred_company_id_filter],
            ),
            missing=colander.drop,
        )
    )
    schema.add(
        colander.SchemaNode(
            colander.Integer(),
            name="supplier_id",
            validator=forms.get_deferred_select_validator(
                Supplier,
                filters=[_deferred_company_id_filter],
            ),
            missing=colander.drop,
        )
    )
    schema.add(
        colander.SchemaNode(colander.String(), name="ref", missing=colander.drop)
    )
    schema.add(
        colander.SchemaNode(
            colander.Boolean(),
            name="simple_only",
            missing=False,
        )
    )
    schema.add(
        colander.SchemaNode(colander.String(), name="mode", missing=colander.drop)
    )
    return schema


def get_stock_operation_add_edit_schema():
    """
    Build a stock operation add edit schema
    """
    schema = SQLAlchemySchemaNode(SaleProductStockOperation)
    return schema

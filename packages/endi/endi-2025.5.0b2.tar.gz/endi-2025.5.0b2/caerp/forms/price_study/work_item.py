import colander
import functools
from colanderalchemy import SQLAlchemySchemaNode
from caerp.models.tva import (
    Tva,
    Product,
)
from caerp.models.task import WorkUnit
from caerp.models.company import Company
from caerp.models.sale_product.base import BaseSaleProduct
from caerp.models.price_study.base import BasePriceStudyProduct
from caerp.models.price_study.work_item import PriceStudyWorkItem
from caerp.utils.html import clean_html
from caerp import forms
from caerp.forms.custom_types import (
    AmountType,
    QuantityType,
)
from caerp.forms.price_study.common import (
    deferred_default_tva_id,
    deferred_default_product_id,
)


def _deferred_company_id_filter(node, kw):
    """
    Build a SQLAlchemy filter for company_id at execution time
    """
    context = kw["request"].context
    if isinstance(context, PriceStudyWorkItem):
        return {"company_id": context.price_study_work.get_company_id()}
    elif isinstance(context, Company):
        return {"company_id": context.id}
    elif isinstance(context, BasePriceStudyProduct):
        return {"company_id": context.get_company_id()}
    else:
        raise Exception("Context is not one of WorkItem, Company {}".format(context))


def customize_work_item_schema(schema, from_work_schema=False, add=False):
    """
    Customize the work item schema to add custom validators and defaults


    :param schema: The schema to customize

    :param bool from_work_schema: Is this customization done a SaleProductWork
    schema, in this case we add special functionnalities

    :return: schema
    """
    customize = functools.partial(forms.customize_field, schema)
    customize("type_", validator=colander.OneOf(BaseSaleProduct.SIMPLE_TYPES))
    customize("description", preparer=clean_html)
    customize("ht", typ=AmountType(5), missing=None)
    customize("supplier_ht", typ=AmountType(5), missing=None)
    customize(
        "unity",
        validator=forms.get_deferred_select_validator(WorkUnit, id_key="label"),
        missing=None,
    )
    customize(
        "_tva_id",
        validator=forms.get_deferred_select_validator(Tva),
        default=deferred_default_tva_id,
        missing=None,
    )
    customize(
        "_product_id",
        validator=forms.get_deferred_select_validator(Product),
        default=deferred_default_product_id,
        missing=None,
    )
    customize(
        "base_sale_product_id",
        validator=forms.get_deferred_select_validator(
            BaseSaleProduct,
            filters=[
                _deferred_company_id_filter,
                BaseSaleProduct.type_.in_(BaseSaleProduct.SIMPLE_TYPES),
            ],
        ),
        missing=colander.drop,
    )
    if "work_item_id" in schema:
        customize("work_item_id", missing=colander.drop)

    if "type_" in schema:
        customize("type_", missing=colander.drop)

    if "work_unit_quantity" in schema:
        customize("work_unit_quantity", typ=QuantityType(), missing=1)
    if "total_quantity" in schema:
        customize("total_quantity", typ=QuantityType())

    if "_margin_rate" in schema:
        customize("_margin_rate", typ=QuantityType(), missing=None)

    # Only edit this field if it's in the submitted datas
    if "quantity_inherited" in schema:
        customize("quantity_inherited", missing=True)

    # On change le nom des noeuds pour passer par les hybrid_attribute de notre
    # modèle (cf la définition de la classe PriceStudyWorkItem)
    for field in ("margin_rate", "tva_id", "product_id"):
        customize("_%s" % field, name=field)

    return schema


def get_work_item_add_edit_schema(add=False):
    EXCLUDES = (
        "work_item",
        "base_sale_product",
        "price_study_work",
        "_product",
        "_tva",
        "price_study_work_id",
        "total_ht",
    )
    schema = SQLAlchemySchemaNode(PriceStudyWorkItem, excludes=EXCLUDES)
    schema = customize_work_item_schema(schema, add=add)
    return schema

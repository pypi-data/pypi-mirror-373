from colanderalchemy import SQLAlchemySchemaNode

from caerp.models.sale_product.category import SaleProductCategory


def get_sale_product_category_add_edit_schema():
    """
    Build an add/edit schema for sale product categories

    :returns: An SQLAlchemySchemaNode
    """
    return SQLAlchemySchemaNode(
        SaleProductCategory,
        includes=("parent_id", "title", "description", "company_id"),
    )

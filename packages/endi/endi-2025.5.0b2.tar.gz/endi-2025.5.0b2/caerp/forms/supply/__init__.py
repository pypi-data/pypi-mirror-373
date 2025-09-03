import colander
import deform
from colanderalchemy import SQLAlchemySchemaNode

from caerp import forms
from caerp.forms.company import company_filter_node_factory
from caerp.forms.custom_types import AmountType
from caerp.forms.lists import BaseListsSchema
from caerp.forms.tasks.invoice import STATUS_OPTIONS
from caerp.forms.third_party.supplier import supplier_filter_node_factory


def _customize_line_schema(schema):
    amount_fields = ["ht", "tva"]
    for field in amount_fields:
        if field in schema:
            forms.customize_field(
                schema,
                field,
                typ=AmountType(2),
                missing=colander.required,
            )
    return schema


def get_add_edit_line_schema(model_class, internal=False, **kwargs):
    """
    :param model_class class: the class we want the line schema for
    """
    if internal:
        kwargs["excludes"] = ("ht", "tva")
    schema = SQLAlchemySchemaNode(model_class, **kwargs)
    _customize_line_schema(schema)
    return schema


def get_list_schema(request, years_func, is_global=False):
    """
    Common to SupplierOrder and SupplierInvoice views

    :param years_func: deferred_function returning a list of years
    :param is_global boolean: is it a CAE-wide listing ?
    """
    schema = BaseListsSchema().clone()
    schema["search"].title = "Nom"
    schema["search"].widget = deform.widget.TextInputWidget(
        attributes={"placeholder": "document / fournisseur"},
    )
    schema.insert(
        1,
        supplier_filter_node_factory(
            name="supplier_id",
            is_global=is_global,
        ),
    )
    # For now, we use task STATUS_OPTIONS
    schema.insert(0, forms.status_filter_node(STATUS_OPTIONS))
    if is_global:
        schema.insert(
            0, company_filter_node_factory(name="company_id", title="Enseigne")
        )
        forms.add_antenne_option_field(request, schema)

    schema.insert(
        0,
        forms.year_filter_node(
            name="year",
            title="Année",
            query_func=years_func,
        ),
    )

    return schema

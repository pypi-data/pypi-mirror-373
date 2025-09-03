"""
Form schemas used to edit an Invoice in progress_invoicing edition mode
"""
import logging

import colander
import colanderalchemy

from caerp.models.task import Invoice
from caerp.models.progress_invoicing import (
    ProgressInvoicingProduct,
    ProgressInvoicingWork,
    ProgressInvoicingWorkItem,
)
from caerp.compute import math_utils
from caerp.forms.tasks.task import get_new_task_name
from caerp.forms.custom_types import (
    QuantityType,
)

from caerp import forms


logger = logging.getLogger(__name__)


def force_two_digits_percent(value):
    """
    Limit a float entry to two digits
    """
    return math_utils.round(value, 2)


@colander.deferred
def deferred_percent_validator(node, kw):
    """
    Return a percent validator for the given context edition
    regarding if it's attached to an Invoice or a CancelInvoice
    """
    context = kw["request"].context
    already_invoiced = context.already_invoiced or 0
    if isinstance(context.task, Invoice):
        to_invoice = math_utils.round(100 - already_invoiced, 2)
        return colander.Range(0, to_invoice)
    else:
        invoiced = already_invoiced
        return colander.Range(-1 * invoiced, 0)


def get_edit_product_schema():
    """
    Build an edition schema used to validate the Product edition

    :returns: An colanderalchemy SQLAlchemySchemaNode object
    """
    schema = colanderalchemy.SQLAlchemySchemaNode(
        ProgressInvoicingProduct,
        includes=(
            "id",
            "percentage",
        ),
    )
    forms.customize_field(
        schema,
        "percentage",
        typ=QuantityType(),
        validator=deferred_percent_validator,
        preparer=force_two_digits_percent,
    )
    return schema


def get_edit_work_schema():
    """
    Build an edition schema used to validate the Work edition

    :returns: An colanderalchemy SQLAlchemySchemaNode object
    """
    schema = colanderalchemy.SQLAlchemySchemaNode(
        ProgressInvoicingWork, includes=("id", "percentage", "locked")
    )
    forms.customize_field(
        schema,
        "percentage",
        typ=QuantityType(),
        validator=deferred_percent_validator,
        preparer=force_two_digits_percent,
    )
    return schema


def get_edit_workitem_schema():
    """
    Build an edition schema used to validate the WorkItem edition

    :returns: An colanderalchemy SQLAlchemySchemaNode object
    """
    schema = colanderalchemy.SQLAlchemySchemaNode(
        ProgressInvoicingWorkItem,
        includes=(
            "id",
            "_percentage",
        ),
    )

    forms.customize_field(
        schema,
        "_percentage",
        typ=QuantityType(),
        validator=deferred_percent_validator,
        preparer=force_two_digits_percent,
    )
    return schema


@colander.deferred
def deferred_default_name(node, kw):
    business = kw["request"].context
    return get_new_task_name(Invoice, business=business)


class NewInvoiceSchema(colander.Schema):
    name = colander.SchemaNode(
        colander.String(),
        title="Nom du document",
        description="Ce nom n'apparaît pas dans le document final",
        validator=colander.Length(max=255),
        default=deferred_default_name,
        missing="Facture",
    )


def get_new_invoice_schema():
    """
    Build a colander schema for invoice add in progressing mode
    """
    return NewInvoiceSchema()

"""
    Form schemas for commercial handling
"""
import datetime
import colander
from deform import widget

from caerp.models.task import invoice
from caerp import forms
from .custom_types import AmountType


def get_years(kw):
    YEAR_MIN = 2000
    years = [year for year in invoice.get_invoice_years() if year >= YEAR_MIN]
    next_year = datetime.date.today().year + 1
    if next_year not in years:
        years.append(next_year)
    return years


class CommercialFormSchema(colander.MappingSchema):
    year = forms.year_select_node(query_func=get_years, title="Année")


class CommercialSetFormSchema(colander.MappingSchema):
    month = colander.SchemaNode(
        colander.Integer(),
        widget=widget.HiddenWidget(),
        title="",
        validator=colander.Range(1, 12),
    )
    value = colander.SchemaNode(AmountType(5), title="CA prévisionnel")
    comment = forms.textarea_node(title="Commentaire", missing="")

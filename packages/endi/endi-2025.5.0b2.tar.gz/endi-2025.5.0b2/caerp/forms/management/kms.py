import deform
import colander
import datetime

from caerp.forms.lists import BaseListsSchema
from caerp.models.expense.sheet import get_expense_years


@colander.deferred
def deferred_year_select(node, kw):
    return deform.widget.SelectWidget(
        values=[(year, year) for year in reversed(get_expense_years(kw))],
        default=datetime.date.today().year,
    )


def get_list_schema():
    schema = BaseListsSchema().clone()
    del schema["search"]
    del schema["page"]
    del schema["items_per_page"]

    schema.add(
        colander.SchemaNode(
            colander.Integer(),
            name="year",
            title="Année",
            widget=deferred_year_select,
        )
    )

    return schema

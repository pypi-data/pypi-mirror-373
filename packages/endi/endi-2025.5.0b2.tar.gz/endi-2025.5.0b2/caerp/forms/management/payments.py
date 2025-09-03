import datetime

from caerp import forms
from caerp.forms.lists import BaseListsSchema


def get_list_schema():
    schema = BaseListsSchema().clone()
    del schema["search"]
    del schema["page"]
    del schema["items_per_page"]

    def get_year_options(kw):
        years = []
        current_year = datetime.date.today().year
        for year in range(current_year - 10, current_year + 1):
            years.append(year)
        return years

    month_node = forms.month_select_node(name="month", title="Mois")
    schema.insert(0, month_node)

    year_node = forms.year_select_node(
        name="year", query_func=get_year_options, title="Année"
    )
    schema.insert(1, year_node)

    return schema

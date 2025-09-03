import deform
import colander

from caerp.forms.lists import BaseListsSchema
from caerp.forms.user import (
    antenne_filter_node_factory,
    follower_filter_node_factory,
)
from caerp.utils.accounting import (
    get_all_financial_year_values,
    get_current_financial_year_value,
    get_financial_year_data,
)


@colander.deferred
def deferred_financial_year_select(node, kw):
    return deform.widget.SelectWidget(
        values=[
            (year, get_financial_year_data(year)["label"])
            for year in get_all_financial_year_values(kw["request"])
        ],
        default=get_current_financial_year_value(),
    )


def get_list_schema():
    schema = BaseListsSchema().clone()
    del schema["search"]
    del schema["page"]
    del schema["items_per_page"]

    schema.add(
        colander.SchemaNode(
            colander.Integer(),
            name="financial_year",
            title="Exercice",
            widget=deferred_financial_year_select,
        )
    )
    schema.add(
        follower_filter_node_factory(
            name="follower_id",
            title="Accompagnateur",
        )
    )
    schema.add(
        antenne_filter_node_factory(
            name="antenne_id",
            title="Antenne",
        )
    )
    schema.add(
        colander.SchemaNode(
            colander.Boolean(),
            name="active",
            label="Masquer les enseignes désactivées",
            arialabel="Activer pour afficher seulement les enseignes actives",
            missing=colander.drop,
        )
    )
    schema.add(
        colander.SchemaNode(
            colander.Boolean(),
            name="internal",
            label="Masquer les enseignes internes",
            arialabel="Activer pour afficher seulement les enseignes non-internes",
            default=True,
            missing=colander.drop,
        )
    )

    return schema

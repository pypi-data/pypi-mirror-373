from caerp import forms
from caerp.models.expense.sheet import get_expense_years
from caerp.forms.user import contractor_filter_node_factory
from caerp.forms.user import follower_filter_node_factory


DOC_STATUS_OPTIONS = (
    ("all", "Tous"),
    ("notjustified", "Justfificatifs en attente"),
    ("justified", "Justficatifs reçus"),
)


def get_list_schema(request):
    """
    Return a schema for invoice validation listing

    Appelé depuis le contexte d'une request, on peut accéder à
    la session de base de données
    """
    schema = forms.lists.BaseListsSchema().clone()
    del schema["search"]
    schema.insert(
        0,
        forms.status_filter_node(
            DOC_STATUS_OPTIONS,
            name="justified_status",
            title="Justificatifs",
        ),
    )
    schema.insert(
        0,
        forms.month_select_node(
            title="Mois",
            missing=-1,
            default=-1,
            name="month",
            widget_options={"default_val": (-1, "Tous")},
        ),
    )
    schema.insert(
        0,
        forms.year_filter_node(
            name="year",
            title="Année",
            query_func=get_expense_years,
        ),
    )
    schema.insert(0, contractor_filter_node_factory(name="owner_id"))
    schema.insert(
        0,
        follower_filter_node_factory(
            name="follower_id",
            title="Accompagnateur",
        ),
    )
    forms.add_antenne_option_field(request, schema)
    return schema

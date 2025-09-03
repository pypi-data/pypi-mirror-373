import colander
import datetime

from caerp import forms
from caerp.forms.company import company_filter_node_factory
from caerp.forms.tasks.invoice import get_invoice_years
from caerp.forms.company import company_choice_node
from caerp.forms.third_party.customer import customer_choice_node_factory
from caerp.models.third_party import Customer


@colander.deferred
def deferred_default_attestations_year(node, kw):
    if datetime.date.today().month > 6:
        return datetime.date.today().year
    else:
        return datetime.date.today().year - 1


def get_list_schema():
    schema = forms.lists.BaseListsSchema().clone()
    schema["search"].title = "Client"
    schema.insert(0, company_filter_node_factory(name="company_id", title="Enseigne"))
    schema.insert(
        0,
        forms.year_filter_node(
            name="year",
            query_func=get_invoice_years,
            title="Année d'attestation",
            default=deferred_default_attestations_year,
        ),
    )
    return schema


def _get_customers_options(*kw):
    from caerp.models.third_party import ThirdParty

    return Customer.label_query().filter(ThirdParty.type == "individual")


class AttestationGenerateSchema(colander.MappingSchema):
    """
    Schema for multiple attestations generate form
    """

    companies_ids = company_choice_node(
        title="Limiter à certaines enseignes",
        description="Laisser vide pour générer pour toutes les enseignes",
        missing=colander.drop,
        multiple=True,
        widget_options=dict(
            active_only=True,
            placeholder="- Sélectionner éventuellement une ou plusieurs enseignes -",
        ),
    )
    customers_ids = customer_choice_node_factory(
        title="Limiter à certains clients",
        description="Laisser vide pour générer pour tous les clients",
        widget_options=dict(
            placeholder="- Sélectionner éventuellement un ou plusieurs clients -",
        ),
        query_func=_get_customers_options,
        multiple=True,
        missing=colander.drop,
    )
    year = forms.year_filter_node(
        name="year",
        query_func=get_invoice_years,
        title="Année d'attestation",
        default=deferred_default_attestations_year,
        missing=colander.required,
    )
    regenerate_existing = colander.SchemaNode(
        colander.Boolean(),
        title="Forcer la re-généreration des attestations existantes",
        default=False,
    )

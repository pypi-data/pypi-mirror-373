"""
Schema used for businesses manipulation
"""

import colander
import deform
import deform_extensions
from colanderalchemy import SQLAlchemySchemaNode

from caerp.consts.permissions import PERMISSIONS
from caerp.services.business import get_invoices_without_deadline

from caerp.forms.custom_types import AmountType
from caerp.forms.lists import BaseListsSchema
from caerp.forms import (
    get_date_input,
    get_deferred_global_default_value,
    year_filter_node,
    add_antenne_option_field,
)

from caerp.forms.company import company_filter_node_factory
from caerp.forms.third_party.customer import customer_filter_node_factory

from caerp.models.project.business import BusinessPaymentDeadline
from caerp.models.task.invoice import get_invoice_years
from caerp.forms.tasks.task import business_type_filter_node


def get_business_list_schema(request, is_global, is_customer_list=False):
    """
    Build the Business list filter schema
    """
    schema = BaseListsSchema().clone()
    schema["search"].title = "Recherche"
    schema[
        "search"
    ].description = "Nom d'affaire, numéro de devis, ou numéro de facture"
    schema.add_before(
        "items_per_page",
        year_filter_node(
            query_func=get_invoice_years,
            title="Année de facturation",
            name="invoicing_year",
        ),
    )
    schema.add_before(
        "items_per_page",
        business_type_filter_node(),
    )
    if is_global:
        schema.add_before(
            "items_per_page", company_filter_node_factory(name="company_id")
        )
    if not is_customer_list:
        schema.add_before(
            "items_per_page",
            customer_filter_node_factory(name="customer_id", is_global=is_global),
        )
    """
    TODO Ajouter un filtre sur l'état des fichiers de l'affaire
    schema.add_before(
        "items_per_page",
        colander.SchemaNode(
            colander.String(),
            title="Indicateurs de fichiers",
            name="sale_file_requirements",
            widget=deform.widget.SelectWidget(
                values=(
                    ("", "Peu importe"),
                    (
                        "danger",
                        "Des fichiers sont manquants",
                    ),
                    (
                        "wait",
                        "Des fichiers sont en attente de validation",
                    ),
                    (
                        "success",
                        "Tous les fichiers ont été fournis",
                    ),
                    (
                        "forced",
                        "Des indicateurs de fichiers ont été forcés",
                    ),
                )
            ),
            missing=colander.drop,
        ),
    )
    """
    schema.add_before(
        "items_per_page",
        colander.SchemaNode(
            colander.String(),
            title="BPF renseigné",
            name="bpf_filled",
            widget=deform.widget.SelectWidget(
                values=(
                    ("", "Peu importe"),
                    ("no", "Non eligible au bpf"),
                    ("yes", "Eligible au bpf (peu importe si renseigné)"),
                    ("full", "Eligible au bpf et bpf renseigne completement"),
                    (
                        "partial",
                        "Eligible au bpf et bpf renseigne partiellement"
                        " ou non renseigné",
                    ),
                )
            ),
            missing=colander.drop,
        ),
    )
    """
    TODO Faire fonctionner le filtre sur l'état de facturation de l'affaire (indicateurs nok)
    schema.add_before(
        "items_per_page",
        colander.SchemaNode(
            colander.Boolean(),
            name="include_completed",
            title="",
            label="Inclure les affaires intégralement facturées",
            default=True,
            missing=True,
        ),
    )
    """
    schema.add_before(
        "items_per_page",
        colander.SchemaNode(
            colander.Boolean(),
            name="include_resulted",
            title="",
            label="Inclure les affaires soldées",
            default=True,
            missing=True,
        ),
    )
    if is_global:
        add_antenne_option_field(request, schema, index=2)
    return schema


@colander.deferred
def deferred_date_modify_widget(node, kw):
    """
    Widget used to edit the date of a BusinessPaymentDeadline
    """
    request = kw["request"]
    if not request.has_permission(
        PERMISSIONS["context.edit_business_payment_deadline.date"], request.context
    ):
        return deform_extensions.DisabledInput()
    else:
        return get_date_input()


def drop_date_if_not_set(schema, kw):
    if kw["request"].context.date is None:
        del schema["date"]
    return schema


def customize_business_payment_deadline_schema(schema, request, fields, invoices):
    if "amount_ttc" in fields:
        schema["amount_ttc"].title = "Montant TTC à facturer"
        schema["amount_ttc"].description = (
            "Montant TTC à facturer : les montants des échéances"
            " doivent correspondre au montant TTC des devis"
            " de l'affaire"
        )
        schema["amount_ttc"].typ = AmountType(precision=5)

    if len(invoices) > 0:
        schema["invoice_id"].title = "Facture"
        schema[
            "invoice_id"
        ].description = "Rattacher la facture qui correspond à cette échéance."

        if request.context.invoice_id:
            schema["invoice_id"].description += (
                " NB : Si vous sélectionnez 'Aucune', la facture associée sera "
                "toujours présente dans l'affaire  (et pourra "
                "être rattachée sur une autre échéance)."
            )

        schema["invoice_id"].widget = deform.widget.SelectWidget(
            values=[("", "Aucune facture")]
            + [
                (invoice.id, f"{invoice.name} - {invoice.official_number}")
                for invoice in invoices
            ]
        )
    return schema


def get_business_payment_deadline_edit_schema(request):
    fields = ("description",)
    invoices = []
    if request.has_permission(
        PERMISSIONS["context.edit_business_payment_deadline.invoice_id"],
        request.context,
    ):
        invoices = []
        invoices.extend(
            get_invoices_without_deadline(request, request.context.business)
        )
        if request.context.invoice:
            invoices.append(request.context.invoice)
        if len(invoices) > 0:
            fields += ("invoice_id",)
    if request.has_permission(
        PERMISSIONS["context.edit_business_payment_deadline.amount"], request.context
    ):
        fields += ("amount_ttc",)
    if request.has_permission(
        PERMISSIONS["context.edit_business_payment_deadline.date"], request.context
    ):
        fields += ("date",)

    schema = SQLAlchemySchemaNode(BusinessPaymentDeadline, includes=fields)
    customize_business_payment_deadline_schema(schema, request, fields, invoices)
    return schema


def get_new_invoice_from_payment_deadline_schema():
    """
    Build the schema used to generate an intermediate
    invoice from a payment deadline
    """
    schema = colander.Schema()
    schema.add(
        colander.SchemaNode(
            colander.Boolean(),
            name="add_estimation_details",
            title="Inclure le détail du devis",
            description=(
                "Inclure le détail du devis (avec des montants à 0) dans la facture"
            ),
            missing=colander.drop,
            default=get_deferred_global_default_value(
                company_attr="default_add_estimation_details_in_invoice",
                default_notfound=False,
            ),
        )
    )
    schema.add(
        colander.SchemaNode(
            colander.Integer(),
            name="deadline_id",
            widget=deform.widget.HiddenWidget(),
        )
    )
    return schema

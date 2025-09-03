"""
    form schemas for invoices related views
"""
import functools
from operator import and_

import colander
import deform
import deform_extensions

from caerp.models.task import Estimation
from caerp.models.tva import Product, Tva
from caerp.models.task.invoice import (
    Invoice,
    CancelInvoice,
    get_invoice_years,
    INVOICE_STATES,
)
from caerp.models.payments import PaymentMode
from caerp.utils.renderer import get_json_dict_repr
from caerp import forms
from caerp.consts.permissions import PERMISSIONS
from caerp.forms.company import company_filter_node_factory
from caerp.forms.third_party.customer import customer_filter_node_factory
from caerp.forms.custom_types import (
    AmountType,
)
from caerp.forms.widgets import FixedLenSequenceWidget
from caerp.forms.widgets import CleanMappingWidget
from caerp.forms.tasks.lists import (
    NumberRangeSchema,
    PeriodSchema,
    AmountRangeSchema,
)
from caerp.forms.tasks.task import (
    get_edit_task_schema,
    business_type_filter_node,
)
from caerp.forms.user import validator_filter_node_factory
from caerp.utils.strings import format_amount

PAID_STATUS_OPTIONS = (
    (
        "all",
        "Tous",
    ),
    (
        "paid",
        "Les factures payées",
    ),
    (
        "notpaid",
        "Seulement les impayés",
    ),
)

STATUS_OPTIONS = (
    (
        "all",
        "Tous",
    ),
    ("draft", "Brouillon"),
    ("wait", "En attente de validation"),
    ("invalid", "Invalide"),
    ("valid", "Valide"),
)

TYPE_OPTIONS = (
    (
        "both",
        "Tous",
    ),
    (
        "invoice",
        "Seulement les factures",
    ),
    (
        "internalinvoice",
        "Seulement les factures internes",
    ),
    (
        "cancelinvoice",
        "Seulement les avoirs",
    ),
    (
        "internalcancelinvoice",
        "Seulement les avoirs internes",
    ),
    (
        "internal",
        "Seulement les factures/avoirs internes",
    ),
    ("external", "Seulement les factures/avoirs externes"),
)


def get_payment_mode_option_list():
    """
    Return structured option list for payment mode widget
    """
    options = [(mode.label, mode.label.title()) for mode in PaymentMode.query()]
    options.append(
        (
            "cancelinvoiced",
            "Avoir",
        )
    )
    options.insert(0, ("all", "Tous"))
    return options


def get_product_choices(document):
    """
    Return data structure for product code select widget options
    """
    query = Product.query()
    query = query.filter(
        and_(
            Product.tva_id.in_(
                Tva.query()
                .with_entities(Tva.id)
                .filter(Tva.value.in_([line.tva for line in document.all_lines]))
            ),
            Product.internal == document.internal,  # noqa: E712
        )
    )
    query = query.order_by(Product.order)
    return [
        (
            p.id,
            "{0} ({1} - {2})".format(p.name, p.compte_cg, p.tva.name),
        )
        for p in query
    ]


@colander.deferred
def deferred_product_validator(node, kw):
    options = [option[0] for option in get_product_choices(kw["request"].context)]
    return colander.OneOf(options)


@colander.deferred
def deferred_product_widget(node, kw):
    """
    return a widget for product selection
    """
    products = get_product_choices(kw["request"].context)
    wid = deform.widget.SelectWidget(values=products)
    return wid


def product_match_tva_validator(form, line_value):
    product_id = line_value.get("product_id")
    product = Product.get(product_id)
    if product.tva.value != line_value["tva"]:
        exc = colander.Invalid(
            form,
            "Le code produit doit correspondre à la TVA associée",
        )
        raise exc


class ProductTaskLine(colander.MappingSchema):
    """
    A single estimation line
    """

    id = colander.SchemaNode(
        colander.Integer(),
        widget=deform.widget.HiddenWidget(),
        missing="",
        css_class="span0",
    )
    description = colander.SchemaNode(
        colander.String(),
        widget=deform.widget.TextInputWidget(readonly=True),
        missing="",
        css_class="col-md-3",
    )
    tva = colander.SchemaNode(
        AmountType(),
        widget=deform_extensions.DisabledInput(),
        css_class="col-md-1",
        title="TVA",
    )
    product_id = colander.SchemaNode(
        colander.Integer(),
        widget=deferred_product_widget,
        validator=deferred_product_validator,
        missing="",
        css_class="col-md-2",
        title="Code produit",
    )


class ProductTaskLines(colander.SequenceSchema):
    taskline = ProductTaskLine(
        missing="",
        title="",
        validator=product_match_tva_validator,
        widget=CleanMappingWidget(),
    )


class SetProductsSchema(colander.MappingSchema):
    """
    Form schema used to configure Products
    """

    lines = ProductTaskLines(widget=FixedLenSequenceWidget(), missing="", title="")


# INVOICE LIST RELATED SCHEMAS
@colander.deferred
def deferred_payment_mode_widget(node, kw):
    return deform.widget.SelectWidget(values=get_payment_mode_option_list())


@colander.deferred
def deferred_payment_mode_validator(node, kw):
    return colander.OneOf([s[0] for s in get_payment_mode_option_list()])


def get_year_options(kw):
    values = get_invoice_years(kw)
    return values


def get_list_schema(request, is_global=False, excludes=()):
    """
    Renvoie un schéma pour lister les factures

    1- Est-ce une liste au niveau global ?
    2- Quels champs supplémentaires exclure ?

    is_global

        Liste de factures globales ?
        Si non on exclue les filtres d'enseigne, d'autovalidation et d'année fiscale de ref
        On restreint aussi le filtre client

    excludes

        Permet d'exclure plus de champs (pour les vues au niveau des enseignes)
        On exclue le client pour les factures d'une affaire par exemple

    """
    schema = forms.lists.BaseListsSchema().clone()

    schema.insert(
        0,
        colander.SchemaNode(
            colander.String(),
            name="payment_mode",
            title="Mode de paiement",
            widget=deferred_payment_mode_widget,
            validator=deferred_payment_mode_validator,
            missing="all",
            default="all",
        ),
    )

    schema.insert(
        0,
        forms.status_filter_node(
            PAID_STATUS_OPTIONS,
            name="paid_status",
            title="Statut de paiement",
        ),
    )

    if not is_global:
        schema.insert(0, forms.status_filter_node(STATUS_OPTIONS))

    if "business_type" not in excludes:
        schema.insert(0, business_type_filter_node())

    schema.insert(
        0,
        colander.SchemaNode(
            colander.String(),
            name="doctype",
            title="Types de factures",
            widget=deform.widget.SelectWidget(values=TYPE_OPTIONS),
            validator=colander.OneOf([s[0] for s in TYPE_OPTIONS]),
            missing="both",
            default="both",
        ),
    )

    schema.insert(
        0,
        AmountRangeSchema(
            name="ttc",
            title="",
            validator=colander.Function(
                forms.range_validator,
                msg=("Le montant minimal doit être inférieur ou égal au maximum"),
            ),
            widget=CleanMappingWidget(),
            missing=colander.drop,
        ),
    )

    if "customer" not in excludes:
        schema.insert(
            0,
            customer_filter_node_factory(
                is_global=is_global,
                name="customer_id",
                title="Client",
                with_invoice=True,
            ),
        )
    if is_global:
        schema.insert(
            0, company_filter_node_factory(name="company_id", title="Enseigne")
        )
        forms.add_antenne_option_field(request, schema)

    if "financial_year" not in excludes:
        node = forms.year_filter_node(
            name="financial_year",
            query_func=get_year_options,
            title="Année fiscale",
        )
        schema.insert(0, node)

    schema.insert(
        0,
        PeriodSchema(
            name="period",
            title="",
            validator=colander.Function(
                forms.range_validator,
                msg="La date de début doit précéder la date de fin",
            ),
            widget=CleanMappingWidget(),
            missing=colander.drop,
        ),
    )

    if "year" not in excludes:
        node = forms.year_filter_node(
            name="year",
            query_func=get_year_options,
            title="Année",
        )
        schema.insert(0, node)

    schema["search"].title = "Numéro de facture"

    if is_global:
        schema.add_before(
            "items_per_page",
            validator_filter_node_factory(
                name="validator_id",
            ),
        )
        schema.add_before(
            "items_per_page",
            colander.SchemaNode(
                colander.Boolean(),
                name="auto_validated",
                label="Documents auto-validés",
                arialabel="Activer pour afficher seulement les documents auto-validés",
                missing=colander.drop,
            ),
        )

    return schema


def get_pdf_export_schema(request):
    title = "Exporter un ensemble de factures dans un fichier pdf"
    schema = colander.Schema(title=title)
    schema.add(
        colander.SchemaNode(
            colander.String(),
            name="doctype",
            title="Types de factures",
            widget=deform.widget.SelectWidget(values=TYPE_OPTIONS),
            validator=colander.OneOf([s[0] for s in TYPE_OPTIONS]),
            missing="both",
            default="both",
        ),
    )
    forms.add_antenne_option_field(request, schema)
    schema.add(company_filter_node_factory(name="company_id", title="Enseigne"))
    schema.add(
        customer_filter_node_factory(
            is_global=True,
            name="customer_id",
            title="Client",
            with_invoice=True,
        ),
    )
    schema.add(
        PeriodSchema(
            name="period",
            title="",
            validator=colander.Function(
                forms.range_validator,
                msg="La date de début doit précéder la date de fin",
            ),
            widget=CleanMappingWidget(),
            missing=colander.drop,
        ),
    )
    schema.add(
        AmountRangeSchema(
            name="ttc",
            title="",
            validator=colander.Function(
                forms.range_validator,
                msg=("Le montant minimal doit être inférieur ou égal au maximum"),
            ),
            widget=CleanMappingWidget(),
            missing=colander.drop,
        ),
    )
    schema.add(
        NumberRangeSchema(
            name="official_number",
            title="",
            widget=CleanMappingWidget(),
            missing=colander.drop,
        )
    )

    schema.add(
        forms.status_filter_node(
            PAID_STATUS_OPTIONS,
            name="paid_status",
            title="Statut de paiement",
        ),
    )
    return schema


@colander.deferred
def deferred_estimation_widget(node, kw):
    """
    Return a select for estimation selection
    """
    invoice = kw["request"].context
    query = Estimation.query()
    query = query.filter(Estimation.project_id == invoice.project_id)
    query = query.filter(Estimation.customer_id == invoice.customer_id)
    query = query.filter(Estimation.business_type_id == invoice.business_type_id)
    choices = []
    for estimation in query:
        amount_label = format_amount(
            estimation.total_ttc(), precision=5, grouping=False
        )
        label = f"{estimation.name} - {amount_label} € TTC"
        choices.append((estimation.id, label))
    choices.insert(0, ("", "Aucun devis"))
    return deform.widget.SelectWidget(values=choices)


class EstimationAttachSchema(colander.Schema):
    estimation_id = colander.SchemaNode(
        colander.Integer(),
        widget=deferred_estimation_widget,
        missing=colander.drop,
        title="Devis à rattacher à cette facture",
    )


def invoice_after_schema_bind(schema, kw):
    """
    Remove financial year node if the user does not have
    the required permission
    """
    request = kw["request"]
    permission = PERMISSIONS["context.set_treasury_invoice"]
    if not request.has_permission(permission):
        if "financial_year" in schema:
            del schema["financial_year"]


def _customize_invoice_schema(schema):
    """
    Add form schema customization to the given Invoice edition schema

    :param obj schema: The schema to edit
    """
    customize = functools.partial(forms.customize_field, schema)
    if "paid_status" in schema:
        customize(
            "paid_status",
            widget=deform.widget.SelectWidget(values=INVOICE_STATES),
            validator=colander.OneOf(list(dict(INVOICE_STATES).keys())),
        )
    if "financial_year" in schema:
        customize("financial_year", widget=deform.widget.TextInputWidget(mask="9999"))
    if "estimation_id" in schema:
        customize("estimation_id", missing=colander.drop)
    schema.after_bind = invoice_after_schema_bind
    return schema


def _customize_cancelinvoice_schema(schema):
    """
    Add form schema customization to the given Invoice edition schema

    :param obj schema: The schema to edit
    """
    customize = functools.partial(forms.customize_field, schema)
    customize("invoice_id", missing=colander.required)
    customize("financial_year", widget=deform.widget.TextInputWidget(mask="9999"))
    return schema


def get_add_edit_invoice_schema(isadmin=False, includes=None, **kw):
    """
    Return add edit schema for Invoice edition

    :param bool isadmin: Are we asking for an admin schema ?
    :param tuple includes: Field that should be included in the schema
    :rtype: `colanderalchemy.SQLAlchemySchemaNode`
    """
    schema = get_edit_task_schema(Invoice, isadmin=isadmin, includes=includes, **kw)
    schema = _customize_invoice_schema(schema)
    return schema


def get_add_edit_cancelinvoice_schema(isadmin=False, includes=None, **kw):
    """
    Return add edit schema for CancelInvoice edition

    :param bool isadmin: Are we asking for an admin schema ?
    :param tuple includes: Field that should be included in the schema
    :rtype: `colanderalchemy.SQLAlchemySchemaNode`
    """
    schema = get_edit_task_schema(
        CancelInvoice, isadmin=isadmin, includes=includes, **kw
    )
    schema = _customize_cancelinvoice_schema(schema)
    return schema


def validate_invoice(invoice_object: "Invoice", request):
    """
    Globally validate an invoice_object

    :param obj invoice_object: An instance of Invoice
    :param obj request: The pyramid request
    :raises: colander.Invalid

    try:
        validate_invoice(est, self.request)
    except colander.Invalid as err:
        error_messages = err.messages
    """
    schema = get_add_edit_invoice_schema()
    schema = schema.bind(request=request)
    appstruct = get_json_dict_repr(invoice_object, request)
    appstruct["line_groups"] = get_json_dict_repr(
        invoice_object.line_groups, request=request
    )
    appstruct["discounts"] = get_json_dict_repr(invoice_object.discounts, request)
    cstruct = schema.deserialize(appstruct)
    return cstruct


def validate_cancelinvoice(cancelinvoice_object: "CancelInvoice", request):
    """
    Globally validate an cancelinvoice_object

    :param obj cancelinvoice_object: An instance of CancelInvoice
    :param obj request: The pyramid request
    :raises: colander.Invalid

    try:
        validate_cancelinvoice(est, self.request)
    except colander.Invalid as err:
        error_messages = err.messages
    """
    schema = get_add_edit_cancelinvoice_schema()
    schema = schema.bind(request=request)
    appstruct = get_json_dict_repr(cancelinvoice_object, request)
    appstruct["line_groups"] = get_json_dict_repr(
        cancelinvoice_object.line_groups, request=request
    )
    cstruct = schema.deserialize(appstruct)
    return cstruct

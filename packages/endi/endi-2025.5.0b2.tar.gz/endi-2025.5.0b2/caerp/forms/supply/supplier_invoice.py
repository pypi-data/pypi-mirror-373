import colander
import deform
import deform_extensions
import functools
import logging

from sqlalchemy import select, distinct, func
from colanderalchemy import SQLAlchemySchemaNode

from caerp import forms
from caerp.compute.math_utils import integer_to_amount
from caerp.controllers.expense_types import ExpenseTypeQueryService
from caerp.forms.company import (
    company_choice_node,
    company_filter_node_factory,
)
from caerp.forms.custom_types import AmountType
from caerp.forms.expense import (
    get_deferred_select_expense_type,
    deferred_type_id_validator,
)
from caerp.forms.files import FileNode
from caerp.forms.payments import (
    deferred_payment_mode_widget,
    deferred_payment_mode_validator,
    deferred_bank_account_widget,
    deferred_bank_account_validator,
)
from caerp.forms.supply import (
    get_add_edit_line_schema,
    get_list_schema,
)
from caerp.forms.supply.supplier_order import (
    get_deferred_supplier_order_select_validator,
    supplier_order_choice_node,
)
from caerp.forms.tasks.lists import (
    PeriodSchema,
    AmountRangeSchema,
)
from caerp.forms.third_party.supplier import (
    get_deferred_supplier_select_validator,
    globalizable_supplier_choice_node_factory,
    supplier_choice_node_factory,
    get_deferred_supplier_choice_validator,
)
from caerp.forms.widgets import (
    FixedLenSequenceWidget,
    CleanMappingWidget,
)
from caerp.models.supply import (
    BaseSupplierInvoicePayment,
    SupplierOrder,
    SupplierInvoice,
    SupplierInvoiceLine,
)
from caerp.utils import strings
from caerp.utils.renderer import get_json_dict_repr
from caerp.services.supplier_invoice import get_supplier_invoices_years


logger = logging.getLogger(__name__)


COMBINED_PAID_STATUS_OPTIONS = (
    ("", "Tous"),
    ("paid", "Les factures soldées"),
    ("supplier_topay", "Fournisseur à payer"),
    ("worker_topay", "Entrepreneur à rembourser"),
)
TYPE_OPTIONS = (
    (
        "both",
        "Tous",
    ),
    (
        "supplier_invoice",
        "Exclure les factures internes",
    ),
    (
        "internalsupplier_invoice",
        "Seulement les factures internes",
    ),
)


# EDIT SCHEMA
@colander.deferred
def deferred_supplier_invoice_cohesion_validator(node: SQLAlchemySchemaNode, kw: dict):
    if "request" not in kw or kw["request"].context is None:
        return None
    request = kw["request"]
    supplier_invoice: SupplierInvoice = kw["request"].context
    validators = []

    def payment_options_validator(_node, values):
        logger.debug("In the supplier_invoice validator")

        if supplier_invoice.payer is None and supplier_invoice.cae_percentage < 100:
            raise colander.Invalid(
                _node,
                "Impossible de valider une facture fournisseur avec une avance "
                "entrepreneur dont l'entrepreneur n'est pas renseigné",
            )

    def supplier_consistency_validator(_node, values):
        """
        Check that supplier_orders belong to the given supplier

        - When we add orders
        - When we change the supplier
        """
        # On récupère soit la valeur déjà configurée, soit celle qui vient d'être submit
        supplier_order_ids = values.get(
            "supplier_orders", [i.id for i in supplier_invoice.supplier_orders]
        )
        supplier_id = values.get("supplier_id", supplier_invoice.supplier_id)
        if len(supplier_order_ids) > 0 and supplier_id is not None:
            id_ = supplier_order_ids[0]
            if (
                request.dbsession.query(SupplierOrder.supplier_id)
                .filter(
                    SupplierOrder.id == id_, SupplierOrder.supplier_id == supplier_id
                )
                .first()
                is None
            ):
                raise colander.Invalid(
                    _node,
                    "Impossible de changer le fournisseur "
                    "d'une facture déjà associée à une ou des commandes.",
                )

    if "payer" in node or "cae_percentage" in node:
        validators.append(payment_options_validator)

    if "supplier_orders" in node or "supplier_id" in node:
        validators.append(supplier_consistency_validator)
    return colander.All(*validators)


def _customize_edit_schema(schema):
    customize = functools.partial(forms.customize_field, schema)

    if "supplier_orders" in schema:
        # On s'assure qu'on sélectionne une liste de type parmis des existants
        # (et qu'on en rajoute pas à la volée)
        customize(
            "supplier_orders",
            children=forms.get_sequence_child_item(
                SupplierOrder,
                child_attrs=("id", "name"),
            ),
            validator=forms.DeferredAll(
                deferred_invoice_orders_validator,
                get_deferred_supplier_order_select_validator(
                    multiple=True,
                    required=False,
                ),
            ),
        )
    if "supplier_id" in schema:
        customize(
            "supplier_id",
            validator=get_deferred_supplier_select_validator(),
            missing=colander.required,
        )

    if "lines" in schema:
        child_schema = schema["lines"].children[0]
        forms.customize_field(child_schema, "type_id", missing=colander.required)

    if "date" in schema:
        schema["date"].missing = colander.required
    if "remote_invoice_number" in schema:
        schema["remote_invoice_number"].missing = colander.required

    schema.validator = deferred_supplier_invoice_cohesion_validator

    return schema


def get_supplier_invoice_edit_schema(internal=False):
    """
    Build the supplier invoice edit schema (via rest api)

    If the supplier invoice is internal, only a few fields can be edited

    :param bool internal: Is the edited document internal ?
    """

    if internal:
        schema = SQLAlchemySchemaNode(
            SupplierInvoice,
            excludes=(
                "name",
                "supplier_orders",
                "supplier_id",
                "payer_id",
                "date",
                "cae_percentage",
                "remote_invoice_number",
            ),
        )
    else:
        schema = SQLAlchemySchemaNode(
            SupplierInvoice,
            excludes=("name",),
        )
    schema = _customize_edit_schema(schema)
    return schema


def validate_supplier_invoice(supplier_invoice_object: SupplierInvoice, request):
    """
    Globally validate an SupplierInvoice

    :param obj invoice_object: An instance of SupplierInvoice
    :param obj request: The pyramid request
    :raises: colander.Invalid

    try:
        validate_supplier_invoice(est, self.request)
    except colander.Invalid as err:
        error_messages = err.messages
    """
    schema = get_supplier_invoice_edit_schema(internal=supplier_invoice_object.internal)
    schema = schema.bind(request=request)

    appstruct = get_json_dict_repr(supplier_invoice_object, request)
    appstruct["lines"] = get_json_dict_repr(
        supplier_invoice_object.lines, request=request
    )
    cstruct = schema.deserialize(appstruct)

    return cstruct


# LIST SCHEMA
def get_supplier_invoice_list_schema(request, is_global=False):
    schema = get_list_schema(
        request,
        years_func=get_supplier_invoices_years,
        is_global=is_global,
    )
    schema.insert(
        1,
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
    schema.insert(
        3,
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
    schema.insert(
        3,
        forms.status_filter_node(
            COMBINED_PAID_STATUS_OPTIONS,
            name="combined_paid_status",
            title="Statut de paiement",
        ),
    )
    schema.insert(
        3,
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
    schema.add_before(
        "items_per_page",
        colander.SchemaNode(
            colander.String(),
            title="N° de pièce",
            name="official_number",
            missing="",
            widget=deform.widget.TextInputWidget(css_class="input-medium search-query"),
            default="",
        ),
    )
    schema.add_before(
        "items_per_page",
        colander.SchemaNode(
            colander.Integer(),
            name="expense_type_id",
            title="Types de dépenses",
            widget=get_deferred_select_expense_type(default=True),
            validator=deferred_type_id_validator,
            missing=-1,
            default=-1,
        ),
    )
    schema.add_before(
        "items_per_page",
        colander.SchemaNode(
            colander.String(),
            title="N° de facture du fournisseur",
            name="remote_invoice_number",
            missing="",
            widget=deform.widget.TextInputWidget(
                css_class="input-medium search-query",
                title="Numéro de facture du fournisseur",
            ),
            default="",
        ),
    )

    del schema["search"]

    return schema


# SUPPLIER INVOICE ADD SCHEMAS
@colander.deferred
def deferred_invoice_orders_validator(node, kw):
    """
    Validate that all supplier orders have the same
    - percentage
    - supplier
    """
    dbsession = kw["request"].dbsession

    def validator(form_node, value):
        supplier_orders_ids = value
        if len(supplier_orders_ids) <= 1:
            return True
        query = (
            select(distinct(SupplierOrder.cae_percentage))
            .where(SupplierOrder.id.in_(supplier_orders_ids))
            .subquery()
        )
        if dbsession.scalar(select(func.count()).select_from(query)) > 1:
            raise colander.Invalid(
                node,
                "Toutes les commandes sélectionnées doivent avoir le même "
                "pourcentage de paiement CAE.",
            )
        query = (
            select(distinct(SupplierOrder.supplier_id))
            .where(SupplierOrder.id.in_(supplier_orders_ids))
            .subquery()
        )
        if dbsession.scalar(select(func.count()).select_from(query)) > 1:
            raise colander.Invalid(
                node,
                "Toutes les commandes sélectionnées doivent avoir le même "
                "fournisseur.",
            )
        return True

    return validator


def get_invoicable_supplier_orders(request):
    company = request.context
    return SupplierOrder.query_for_select(
        valid_only=True, invoiced=False, company_id=company.id
    )


class SupplierInvoiceAddByOrdersSchema(colander.MappingSchema):
    supplier_orders_ids = supplier_order_choice_node(
        title="Commande(s) fournisseur",
        multiple=True,
        missing=colander.drop,
        description=(
            "Vous pouvez associer votre facture à une ou "
            + "plusieurs commandes préalablement validées. "
            + "Les lignes des commandes seront importées dans la facture."
        ),
        query_func=get_invoicable_supplier_orders,
        extra_validator=deferred_invoice_orders_validator,
    )


def get_supplier_invoice_add_by_supplier_schema():
    schema = SQLAlchemySchemaNode(
        SupplierInvoice,
        includes=["supplier_id"],
    )
    schema["supplier_id"] = supplier_choice_node_factory(
        description="Si le fournisseur manque, l'ajouter d'abord "
        "dans Achats → Fournisseurs."
    )
    schema.validator = get_deferred_supplier_choice_validator()
    return schema


# PAIEMENT
def _invoice_from_request(request) -> SupplierInvoice:
    if type(request.context) is SupplierInvoice:
        supplier_invoice = request.context
    else:
        supplier_invoice = request.context.supplier_invoice
    return supplier_invoice


def _invoice_cae_amount_from_request(request):
    max_amount = _invoice_from_request(request).cae_topay()
    # for edit schema:
    if isinstance(request.context, BaseSupplierInvoicePayment):
        max_amount += request.context.get_amount()
    return max_amount


def _invoice_worker_amount_from_request(request):
    max_amount = _invoice_from_request(request).worker_topay()
    # for edit schema:
    if isinstance(request.context, BaseSupplierInvoicePayment):
        max_amount += request.context.get_amount()
    return max_amount


@colander.deferred
def deferred_payment_cae_amount_validator(node, kw):
    """
    Validate the amount to keep the sum under the of what CAE sohuld pay.
    """
    topay = _invoice_cae_amount_from_request(kw["request"])
    invoice = _invoice_from_request(kw["request"])
    if invoice.total > 0:
        max_value = topay
        min_value = 0
        max_msg = "Le montant payé par la CAE ne doit pas dépasser {}".format(
            integer_to_amount(topay)
        )
        min_msg = "Le montant doit être positif"
    else:
        max_value = 0
        min_value = topay
        max_msg = "Le montant doit être négatif"
        min_msg = "Le montant payé par la CAE ne doit pas dépasser {}".format(
            integer_to_amount(topay)
        )

    return colander.Range(
        min=min_value,
        max=max_value,
        min_err=min_msg,
        max_err=max_msg,
    )


@colander.deferred
def deferred_payment_worker_amount_validator(node, kw):
    """
    Validate the amount to keep the sum under the of what CAE sohuld pay.
    """
    topay = _invoice_worker_amount_from_request(kw["request"])
    invoice = _invoice_from_request(kw["request"])
    if invoice.total > 0:
        max_value = topay
        min_value = 0
        max_msg = (
            "Le montant payé par l'entrepreneur-euse ne doit pas dépasser "
            "{}".format(integer_to_amount(topay))
        )
        min_msg = "Le montant doit être positif"
    else:
        max_value = 0
        min_value = topay
        max_msg = "Le montant doit être négatif"
        min_msg = (
            "Le montant payé par l'entrepreneur-euse ne doit pas dépasser "
            "{}".format(integer_to_amount(topay))
        )

    return colander.Range(
        min=min_value,
        max=max_value,
        min_err=min_msg,
        max_err=max_msg,
    )


@colander.deferred
def deferred_payment_cae_amount_default(node, kw):
    return _invoice_cae_amount_from_request(kw["request"])


@colander.deferred
def deferred_payment_worker_amount_default(node, kw):
    return _invoice_worker_amount_from_request(kw["request"])


class BaseSupplierInvoicePaymentSchema(colander.MappingSchema):
    amount = colander.SchemaNode(
        AmountType(),
    )
    come_from = forms.come_from_node()
    date = forms.today_node()

    mode = colander.SchemaNode(
        colander.String(),
        title="Mode de paiement",
        widget=deferred_payment_mode_widget,
        validator=deferred_payment_mode_validator,
    )
    bank_id = colander.SchemaNode(
        colander.Integer(),
        title="Banque",
        widget=deferred_bank_account_widget,
        validator=deferred_bank_account_validator,
    )
    resulted = colander.SchemaNode(
        colander.Boolean(),
        title="Soldé",
        description=(
            "Indique que le document est soldé (ne recevra plus de paiement), "
            + "si le montant indiqué correspond au montant de la facture "
            + "fournisseur, celui-ci est soldée automatiquement."
        ),
        missing=False,
        default=False,
    )
    bank_remittance_id = colander.SchemaNode(
        colander.String(),
        title="Référence du paiement",
        description=(
            "Ce champ est un indicateur permettant de retrouver l'opération "
            + "bancaire à laquelle ce décaissement est associé, par exemple "
            + "pour la communiquer à un fournisseur"
        ),
        missing="",
    )


class SupplierPaymentSchema(BaseSupplierInvoicePaymentSchema):
    amount = colander.SchemaNode(
        AmountType(),
        title="Montant du paiement",
        validator=deferred_payment_cae_amount_validator,
        default=deferred_payment_cae_amount_default,
    )


class UserPaymentSchema(BaseSupplierInvoicePaymentSchema):
    amount = colander.SchemaNode(
        AmountType(),
        title="Montant du remboursement",
        validator=deferred_payment_worker_amount_validator,
        default=deferred_payment_worker_amount_default,
    )
    waiver = colander.SchemaNode(
        colander.Boolean(),
        title="Abandon de créance",
        description="""Indique que ce paiement correspond à un abandon de créance à la hauteur du
montant indiqué, le mode de paiement, la référence de paiement et la banque
sont alors ignorés""",
        missing=False,
        default=False,
        toggle=False,
    )


INVOICE_LINE_GRID = (
    (
        ("company_id", 3),
        ("type_id", 4),
        ("description", 3),
        ("ht", 1),
        ("tva", 1),
    ),
)


# INVOICE DISPATCH SCHEMA
def _purchase_type_query_builder(kw: dict):
    """
    Construit une query pour récupérer les types d'achats.
    Est appelé depuis un colander.deferred

    :param kw: binding arguments utilisés à la création du formulaire
    """
    logger.debug("Current context: %s", kw["request"].context)
    if getattr(kw["request"].context, "internal", False):

        return ExpenseTypeQueryService.purchase_options(internal=True)
    else:
        return ExpenseTypeQueryService.purchase_options(internal=False)


@colander.deferred
def deferred_purchase_options_select(node, kw):
    query = _purchase_type_query_builder(kw)
    options = forms.get_choice_node_widget_options(
        resource_name="type_id",
        title="Type d'achat",
        placeholder="Sélectionnez un type",
    )
    choices = [
        (i.id, i.display_label)
        for i in kw["request"].dbsession.execute(query).scalars().all()
    ]
    choices.insert(0, ("", "- Sélectionnez un type -"))

    return deform.widget.Select2Widget(values=choices, **options)


def get_supplier_invoice_line_dispatch_schema():
    schema = get_add_edit_line_schema(
        SupplierInvoiceLine,
        widget=deform_extensions.GridMappingWidget(named_grid=INVOICE_LINE_GRID),
        title="ligne",
        excludes=["type_id", "business_id", "project_id", "customer_id"],
    )
    forms.customize_field(
        schema,
        "tva",
        title="TVA",
        validator=colander.Range(min=0),
    )
    forms.customize_field(
        schema,
        "ht",
        title="HT",
        validator=colander.Range(min=0),
    )
    schema.add(
        company_choice_node(
            name="company_id",
            title="Enseigne",
        )
    )
    schema.add(
        colander.SchemaNode(
            typ=colander.Integer(),
            name="type_id",
            title="Type d'achat",
            widget=deferred_purchase_options_select,
        )
    )

    return schema


class DispatchInvoiceLineSequenceSchema(colander.SequenceSchema):
    lines = get_supplier_invoice_line_dispatch_schema()


def _get_linkable_lines(node, kw):
    business = kw["request"].context
    assert business.__name__ == "business"
    return SupplierInvoiceLine.linkable(business)


def _get_deferred_supplier_invoice_line_choices(widget_options):
    default_option = widget_options.pop("default_option", None)

    @colander.deferred
    def deferred_supplier_invoice_line_choices(node, kw):
        query = _get_linkable_lines(node, kw)
        # most recent first
        query = query.order_by(
            SupplierInvoice.date.desc(),
            SupplierInvoice.id.desc(),
        )
        values = [(v.id, v.long_label()) for v in query]
        if default_option:
            # Use of placeholder arg is mandatory with Select2 ; otherwise, the
            # clear button crashes. https://github.com/select2/select2/issues/5725
            # Cleaner fix would be to replace `default_option` 2-uple arg with
            # a `placeholder` str arg, as in JS code.
            values.insert(0, default_option)
            widget_options["placeholder"] = default_option[1]
        return deform.widget.Select2Widget(values=values, **widget_options)

    return deferred_supplier_invoice_line_choices


def supplier_invoice_line_node(multiple=False, **kw):
    widget_options = kw.pop("widget_options", {})
    widget_options.setdefault("default_option", ("", ""))
    return colander.SchemaNode(
        colander.Set() if multiple else colander.Integer(),
        widget=_get_deferred_supplier_invoice_line_choices(widget_options),
        validator=forms.deferred_id_validator(
            _get_linkable_lines,
        ),
        **kw,
    )


supplier_invoice_line_choice_node = forms.mk_choice_node_factory(
    supplier_invoice_line_node,
    resource_name="une ligne de facture fournisseur",
)


class SupplierInvoiceLineSeq(colander.SequenceSchema):
    line = supplier_invoice_line_choice_node()


class SupplierInvoiceDispatchSchema(colander.MappingSchema):
    date = colander.SchemaNode(colander.Date())
    invoice_file = FileNode(title="Document")
    supplier_id = globalizable_supplier_choice_node_factory(
        description=(
            "Seuls les fournisseurs présents dans au moins une enseigne "
            + "et avec un n° d'immatriculation renseigné sont proposés. Si "
            + "un fournisseur est manquant, il faudra commencer par le "
            + "saisir dans les fournisseurs d'une enseigne."
        )
    )
    total_ht = colander.SchemaNode(
        AmountType(),
        title="Total HT",
        validator=colander.Range(min=0),
    )

    total_tva = colander.SchemaNode(
        AmountType(),
        title="Total TVA",
        validator=colander.Range(min=0),
    )

    lines = DispatchInvoiceLineSequenceSchema(
        title="Lignes de facture",
        widget=deform.widget.SequenceWidget(min_len=1),
    )

    remote_invoice_number = colander.SchemaNode(
        colander.String(),
        missing=colander.drop,
        title="Numéro de facture",
        description="Tel que mentionné sur le document du fournisseur",
    )

    def _validate_sum(self, line_fieldname, total_fieldname, values):
        """
        :rtype list:
        :return: the SchemaNodes with an error
        """
        total = values.get(total_fieldname)
        lines_sum = sum(line[line_fieldname] for line in values["lines"])
        return total == lines_sum

    def validator(self, form, values):
        # the error is not very detailed as the user should already have been
        # noticed front-end side (JS).
        valid = self._validate_sum("ht", "total_ht", values) and self._validate_sum(
            "tva", "total_tva", values
        )
        if not valid:
            raise colander.Invalid(form, msg="Totaux incohérents")


# After validation Product configuration schemas
class ProductSupplierInvoiceLine(colander.MappingSchema):
    """
    A single supplier invoice line
    """

    id = colander.SchemaNode(
        colander.Integer(),
        widget=deform.widget.HiddenWidget(),
        missing="",
        css_class="span0",
    )
    description = colander.SchemaNode(
        colander.String(),
        title="Description",
        widget=deform.widget.TextInputWidget(readonly=True),
        missing="",
        css_class="col-md-3",
    )
    type_id = colander.SchemaNode(
        colander.Integer(),
        title="Type d'achat",
        widget=deferred_purchase_options_select,
        css_class="span0",
    )


class ProductSupplierInvoiceLines(colander.SequenceSchema):
    taskline = ProductSupplierInvoiceLine(
        missing="",
        title="",
        widget=CleanMappingWidget(),
    )


class SetTypesSchema(colander.MappingSchema):
    """
    Form schema used to configure Products
    """

    lines = ProductSupplierInvoiceLines(
        widget=FixedLenSequenceWidget(), missing="", title=""
    )


def get_files_export_schema():
    title = "Exporter une archive de justificatifs d'achat"
    schema = colander.Schema(title=title)
    schema.add(company_filter_node_factory(name="owner_id", title="Enseigne"))
    schema.add(
        forms.month_select_node(
            title="Mois",
            missing=-1,
            default=-1,
            name="month",
            widget_options={"default_val": (-1, "Tous")},
        ),
    )
    schema.add(
        forms.year_select_node(
            name="year",
            title="Année",
            query_func=get_supplier_invoices_years,
        ),
    )
    return schema


def get_sepa_waiting_schema(sheet):
    topay = sheet.cae_amount_waiting_for_payment()
    topay_label = strings.format_amount(topay, html=False, currency=True)

    class SEPAWaitingSchema(colander.Schema):
        full = colander.SchemaNode(
            colander.Boolean(),
            title=f"En totalité ({topay_label})",
            missing=False,
            default=True,
            description="Mettre l'ensemble de la somme à payer (décocher pour spécifier un montant partiel)",
            widget=deform_extensions.CheckboxToggleWidget(
                true_target="", false_target="amount"
            ),
        )
        amount = colander.SchemaNode(
            AmountType(),
            title="Montant",
            required=True,
            default=topay,
            validator=colander.Range(
                min=1,
                max=topay,
                min_err="Merci de saisir un montant supérieur à 0",
                max_err="Merci de saisir un montant inférieur ou égal à "
                f"{topay_label}",
            ),
        )

    return SEPAWaitingSchema()

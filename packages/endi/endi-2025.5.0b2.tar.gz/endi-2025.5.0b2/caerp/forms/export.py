import colander
import deform

from deform_extensions import GridFormWidget

from caerp import forms
from caerp.forms.company import company_filter_node_factory
from caerp.forms.lists import BaseListsSchema
from caerp.forms.tasks.lists import existing_invoice_official_number_validator
from caerp.forms.user import (
    contractor_filter_node_factory,
    validator_filter_node_factory,
    issuer_filter_node_factory,
    antenne_filter_node_factory,
    follower_filter_node_factory,
)
from caerp.models.expense.sheet import get_expense_years
from caerp.models.payments import PaymentMode, BankAccount
from caerp.models.task.invoice import get_invoice_years
from caerp.models.task import Task
from caerp.models.user.user import User
from caerp.utils.compat import Iterable


class InvoicesRangeSchema(colander.MappingSchema):
    """
    Form schema for an invoice number selection (year + number)
    """

    financial_year = forms.year_filter_node(
        title="Année comptable",
        query_func=get_invoice_years,
        widget_options={"default_val": ("", "Sélectionner une année")},
        missing=colander.required,
    )
    start = colander.SchemaNode(
        colander.String(),
        title="Depuis la facture numéro",
        description="Numéro de facture à partir duquel exporter",
    )
    end = colander.SchemaNode(
        colander.String(),
        title="Jusqu'à la facture numéro",
        description=(
            "Numéro de facture jusqu'auquel exporter (dernier document si vide)"
        ),
        missing=colander.null,
    )
    doctypes = colander.SchemaNode(
        colander.String(),
        title="Type de document à inclure",
        default="all",
        missing="all",
        widget=deform.widget.RadioChoiceWidget(
            values=(
                ("all", "Toutes les factures"),
                ("internal", "Seules les factures internes"),
                ("external", "Exclure les factures internes"),
            )
        ),
    )

    def validator(self, form, value):
        """
        Validate the number range
        """
        year = value["financial_year"]
        start_num = value["start"]
        end_num = value["end"]

        if not existing_invoice_official_number_validator(start_num, year):
            exc = colander.Invalid(
                form,
                "Aucune facture {} n'est rattachée à l'année {}".format(
                    start_num, year
                ),
            )
            exc["start"] = "Aucune facture n'existe avec ce n° de facture"
            raise exc

        if end_num != colander.null:
            if not existing_invoice_official_number_validator(end_num, year):
                exc = colander.Invalid(
                    form,
                    "Aucune facture {} n'est rattachée à l'année {}".format(
                        end_num, year
                    ),
                )
                exc["start"] = "Aucune facture n'existe avec ce n° de facture"
                raise exc

            start_time = Task.find_task_status_date(start_num, year)
            end_time = Task.find_task_status_date(end_num, year)

            if start_time > end_time:
                exc = colander.Invalid(
                    form,
                    "Le numéro de début doit être plus petit ou égal à celui de fin",
                )
                exc["start"] = "Doit être inférieur au numéro de fin"
                raise exc


@colander.deferred
def deferred_category(node, kw):
    return kw.get("prefix", "0")


class CategoryNode(colander.SchemaNode):
    schema_type = colander.String
    widget = deform.widget.HiddenWidget()
    default = deferred_category


class ExportedFieldNode(colander.SchemaNode):
    schema_type = colander.Boolean
    label = "Inclure les éléments déjà exportés ?"

    description = (
        "enDI retient les éléments qui ont déjà été "
        "exportés, vous pouvez décider ici de les inclure"
    )
    default = False
    missing = False
    widget = deform.widget.CheckboxWidget(toggle=False)


class OnlyAutoValidatedFieldNode(colander.SchemaNode):
    schema_type = colander.Boolean
    label = "Uniquement les documents autovalidés ?"

    description = (
        "Si vous cochez cette case, seule les écritures provenant"
        " de documents autovalidés seront exportées."
    )
    default = False
    missing = False
    widget = deform.widget.CheckboxWidget(toggle=False)


class PeriodSchema(colander.MappingSchema):
    """
    A form used to select a period
    """

    start_date = colander.SchemaNode(colander.Date(), title="Date de début")
    end_date = colander.SchemaNode(
        colander.Date(),
        title="Date de fin",
        missing=forms.deferred_today,
        default=forms.deferred_today,
    )
    exported = ExportedFieldNode()
    antenne_id = antenne_filter_node_factory()
    follower_id = follower_filter_node_factory()

    def validator(self, form, value):
        """
        Validate the period
        """
        if value["start_date"] > value["end_date"]:
            exc = colander.Invalid(
                form, "La date de début doit précéder la date de fin"
            )
            exc["start_date"] = "Doit précéder la date de fin"
            raise exc


class AllSchema(colander.MappingSchema):
    antenne_id = antenne_filter_node_factory()
    follower_id = follower_filter_node_factory()


class InvoiceDoctypeNode(colander.SchemaNode):
    schema_type = colander.String
    widget = deform.widget.RadioChoiceWidget(
        values=(
            ("all", "Toutes les factures"),
            ("internal", "Seules les factures internes"),
            ("external", "Exclure les factures internes"),
        )
    )
    title = ""
    default = "all"
    missing = "all"


class InvoiceNumberSchema(InvoicesRangeSchema):
    """Extends the date+number selector

    With filter on accountancy export status.
    """

    widget = GridFormWidget(
        named_grid=[
            [("financial_year", 4), ("start", 4), ("end", 4)],
            [("exported", 12)],
            [("doctypes", 12)],
            [("validator_id", 6), ("only_auto_validated", 6)],
            [("antenne_id", 6), ("follower_id", 6)],
        ]
    )
    exported = ExportedFieldNode(insert_before="doctypes")
    only_auto_validated = OnlyAutoValidatedFieldNode()
    doctypes = InvoiceDoctypeNode()
    validator_id = validator_filter_node_factory()
    antenne_id = antenne_filter_node_factory()
    follower_id = follower_filter_node_factory()


class InvoicePeriodSchema(PeriodSchema):
    widget = GridFormWidget(
        named_grid=[
            [("start_date", 6), ("end_date", 6)],
            [("exported", 12)],
            [("doctypes", 12)],
            [("validator_id", 6), ("only_auto_validated", 6)],
            [("antenne_id", 6), ("follower_id", 6)],
        ]
    )
    doctypes = InvoiceDoctypeNode()
    only_auto_validated = OnlyAutoValidatedFieldNode()
    validator_id = validator_filter_node_factory()


class InvoiceAllSchema(AllSchema):
    widget = GridFormWidget(
        named_grid=[
            [("exported", 12)],
            [("doctypes", 12)],
            [("validator_id", 6), ("only_auto_validated", 6)],
            [("antenne_id", 6), ("follower_id", 6)],
        ]
    )
    title = "Exporter les factures non exportées"
    doctypes = InvoiceDoctypeNode()
    only_auto_validated = OnlyAutoValidatedFieldNode()
    validator_id = validator_filter_node_factory()


class PaymentDoctypeNode(InvoiceDoctypeNode):
    widget = deform.widget.RadioChoiceWidget(
        values=(
            ("all", "Tous les encaissements"),
            ("internal", "Seuls les encaissements des factures internes"),
            ("external", "Exclure les encaissements factures internes"),
        )
    )


@colander.deferred
def deferred_payment_mode_widget(node, kw):
    modes = [(mode.label, mode.label) for mode in PaymentMode.query()]
    modes.insert(0, ("", "Tous"))
    return deform.widget.Select2Widget(
        values=modes, placeholder="Tous", empty_filter_msg="Tous"
    )


class PaymentModeNode(colander.SchemaNode):
    schema_type = colander.String
    title = "Mode de paiement"
    widget = deferred_payment_mode_widget
    missing = colander.drop
    default = ""


@colander.deferred
def deferred_bank_account_widget(node, kw):
    accounts = [
        (account.id, account.label)
        for account in BankAccount.query().filter(BankAccount.active == 1)
    ]
    accounts.insert(0, ("0", "Tous"))
    return deform.widget.Select2Widget(
        values=accounts, placeholder="Tous", empty_filter_msg="Tous"
    )


class BankAccountNode(colander.SchemaNode):
    schema_type = colander.Integer
    title = "Compte bancaire"
    widget = deferred_bank_account_widget
    missing = colander.drop
    default = "0"


class PaymentAllSchema(AllSchema):
    widget = GridFormWidget(
        named_grid=[
            [("doctypes", 12)],
            [("issuer_id", 6), ("only_auto_validated", 6)],
            [("mode", 6), ("bank_account", 6)],
            [("antenne_id", 6), ("follower_id", 6)],
        ]
    )
    title = "Exporter les encaissements non exportées"
    doctypes = PaymentDoctypeNode()
    issuer_id = issuer_filter_node_factory()
    mode = PaymentModeNode()
    bank_account = BankAccountNode()


class PaymentPeriodSchema(PeriodSchema):
    widget = GridFormWidget(
        named_grid=[
            [("start_date", 6), ("end_date", 6)],
            [("exported", 12)],
            [("doctypes", 12)],
            [("issuer_id", 6)],
            [("mode", 6), ("bank_account", 6)],
            [("antenne_id", 6), ("follower_id", 6)],
        ]
    )

    title = "Exporter les encaissements des factures sur une période donnée"
    doctypes = PaymentDoctypeNode()
    issuer_id = issuer_filter_node_factory()
    mode = PaymentModeNode()
    bank_account = BankAccountNode()


class ExpenseAllSchema(AllSchema):
    widget = GridFormWidget(
        named_grid=[
            [("year", 6), ("month", 6)],
            [("user_id", 6)],
            [("exported", 12)],
            [("category", 12)],
            [("validator_id", 6)],
            [("antenne_id", 6), ("follower_id", 6)],
        ]
    )
    category = CategoryNode()
    validator_id = validator_filter_node_factory()
    antenne_id = antenne_filter_node_factory(title="Antenne de rattachement de l'ES")
    follower_id = follower_filter_node_factory(title="Accompagnateur de l'ES")
    mode = PaymentModeNode()


class ExpenseSchema(colander.MappingSchema):
    """
    Schema for sage expense export
    """

    widget = GridFormWidget(
        named_grid=[
            [("year", 6), ("month", 6)],
            [("user_id", 6)],
            [("exported", 12)],
            [("category", 12)],
            [("validator_id", 6)],
            [("antenne_id", 6), ("follower_id", 6)],
        ]
    )
    user_id = contractor_filter_node_factory()
    year = forms.year_select_node(title="Année", query_func=get_expense_years)
    month = forms.month_select_node(title="Mois")
    exported = ExportedFieldNode()
    category = CategoryNode()
    validator_id = validator_filter_node_factory()
    antenne_id = antenne_filter_node_factory(title="Antenne de rattachement de l'ES")
    follower_id = follower_filter_node_factory(title="Accompagnateur de l'ES")


class ExpenseNumberSchema(colander.MappingSchema):
    widget = GridFormWidget(
        named_grid=[
            [("official_number", 6)],
            [("exported", 12)],
            [("category", 12)],
            [("validator_id", 6)],
            [("antenne_id", 6), ("follower_id", 6)],
        ]
    )
    official_number = colander.SchemaNode(
        colander.String(),
        title="N° de pièce",
        description="N° de pièce de la note de dépenses " "(voir sur la page associée)",
    )
    exported = ExportedFieldNode()
    category = CategoryNode()
    validator_id = validator_filter_node_factory()
    antenne_id = antenne_filter_node_factory(title="Antenne de rattachement de l'ES")
    follower_id = follower_filter_node_factory(title="Accompagnateur de l'ES")


class ExpensePaymentAllSchema(AllSchema):
    widget = GridFormWidget(
        named_grid=[
            [("user_id", 6)],
            [("doctypes", 12)],
            [("issuer_id", 6)],
            [("mode", 6), ("bank_account", 6)],
            [("antenne_id", 6), ("follower_id", 6)],
        ]
    )
    title = "Exporter les paiements des notes de dépenses non exportés"
    doctypes = PaymentDoctypeNode()
    issuer_id = issuer_filter_node_factory()
    antenne_id = antenne_filter_node_factory(title="Antenne de rattachement de l'ES")
    follower_id = follower_filter_node_factory(title="Accompagnateur de l'ES")
    mode = PaymentModeNode()
    bank_account = BankAccountNode()


class ExpensePaymentPeriodSchema(PeriodSchema):
    widget = GridFormWidget(
        named_grid=[
            [("start_date", 6), ("end_date", 6)],
            [("exported", 12)],
            [("doctypes", 12)],
            [("issuer_id", 6)],
            [("mode", 6), ("bank_account", 6)],
            [("antenne_id", 6), ("follower_id", 6)],
        ]
    )
    title = "Exporter les paiements des notes de dépenses sur la période \
donnée"
    doctypes = PaymentDoctypeNode()
    issuer_id = issuer_filter_node_factory()
    antenne_id = antenne_filter_node_factory(title="Antenne de rattachement de l'ES")
    follower_id = follower_filter_node_factory(title="Accompagnateur de l'ES")
    mode = PaymentModeNode()
    bank_account = BankAccountNode()


class SupplierInvoiceDoctypeNode(InvoiceDoctypeNode):
    widget = deform.widget.RadioChoiceWidget(
        values=(
            ("all", "Toutes les factures fournisseurs"),
            ("internal", "Seules les factures internes"),
            ("external", "Exclure les factures internes"),
        )
    )


class SupplierInvoiceAllSchema(AllSchema):
    widget = GridFormWidget(
        named_grid=[
            [("doctypes", 12)],
            [("validator_id", 6)],
            [("antenne_id", 6), ("follower_id", 6)],
        ]
    )
    title = "Exporter les factures fournisseurs non exportées"
    doctypes = SupplierInvoiceDoctypeNode()
    validator_id = validator_filter_node_factory()


class SupplierInvoicePeriodSchema(PeriodSchema):
    widget = GridFormWidget(
        named_grid=[
            [("start_date", 6), ("end_date", 6)],
            [("exported", 12)],
            [("doctypes", 12)],
            [("validator_id", 6)],
            [("antenne_id", 6), ("follower_id", 6)],
        ]
    )
    title = "Exporter les factures fournisseurs sur une période donnée"
    doctypes = SupplierInvoiceDoctypeNode()
    validator_id = validator_filter_node_factory()


class SupplierInvoiceSchema(colander.MappingSchema):
    """
    Schema for sage supplier invoice export
    """

    widget = GridFormWidget(
        named_grid=[
            [("company_id", 6)],
            [("exported", 12)],
            [("doctypes", 12)],
            [("validator_id", 6)],
            [("antenne_id", 6), ("follower_id", 6)],
        ]
    )

    title = "Exporter les factures fournisseurs par enseigne"
    company_id = company_filter_node_factory()
    doctypes = SupplierInvoiceDoctypeNode()
    exported = ExportedFieldNode()
    validator_id = validator_filter_node_factory()


class SupplierInvoiceNumberSchema(colander.MappingSchema):
    widget = GridFormWidget(
        named_grid=[
            [("official_number", 6)],
            [("exported", 12)],
            [("validator_id", 6)],
        ]
    )
    official_number = colander.SchemaNode(
        colander.String(),
        title="N° de pièce",
        description=(
            "Numéro de pièce de la facture fournisseur " "(voir sur la page associée)"
        ),
    )
    exported = ExportedFieldNode()
    validator_id = validator_filter_node_factory()


class SupplierPaymentDoctypeNode(InvoiceDoctypeNode):
    widget = deform.widget.RadioChoiceWidget(
        values=(
            ("all", "Tous les paiements"),
            ("internal", "Seuls les paiements des factures fournisseurs internes"),
            ("external", "Exclure les paiements des factures fournisseurs internes"),
        )
    )


class SupplierPaymentNumberSchema(colander.MappingSchema):
    widget = GridFormWidget(
        named_grid=[
            [("official_number", 6)],
            [("exported", 12)],
            [("issuer_id", 6)],
        ]
    )
    title = "Exporter les paiements d'une facture fournisseur"

    official_number = colander.SchemaNode(
        colander.String(),
        title="N° de pièce",
        description=(
            "Numéro de pièce de la facture fournisseur " "(voir sur la page associée)"
        ),
    )
    exported = ExportedFieldNode()
    issuer_id = issuer_filter_node_factory()


class SupplierPaymentAllSchema(AllSchema):
    widget = GridFormWidget(
        named_grid=[
            [("exported", 12)],
            [("doctypes", 12)],
            [("issuer_id", 6)],
            [("mode", 6), ("bank_account", 6)],
            [("antenne_id", 6), ("follower_id", 6)],
        ]
    )
    title = "Exporter les paiements fournisseurs non exportés"
    doctypes = SupplierPaymentDoctypeNode()
    issuer_id = issuer_filter_node_factory()
    mode = PaymentModeNode()
    bank_account = BankAccountNode()


class SupplierPaymentPeriodSchema(PeriodSchema):
    widget = GridFormWidget(
        named_grid=[
            [("start_date", 6), ("end_date", 6)],
            [("exported", 12)],
            [("doctypes", 12)],
            [("issuer_id", 6)],
            [("mode", 6), ("bank_account", 6)],
            [("antenne_id", 6), ("follower_id", 6)],
        ]
    )
    title = "Exporter les paiements fournisseurs d'une période donnée"
    doctypes = SupplierPaymentDoctypeNode()
    issuer_id = issuer_filter_node_factory()
    mode = PaymentModeNode()
    bank_account = BankAccountNode()


class BPFYearSchema(colander.MappingSchema):
    """
    Schema for BPF export (agregate of BusinessBPFData)
    """

    year = forms.year_select_node(
        title="Année",
        query_func=get_expense_years,
    )
    company_id = company_filter_node_factory()
    ignore_missing_data = colander.SchemaNode(
        colander.Boolean(),
        title="Forcer l'export",
        description="Ignorer les éléments dont le BPF n'est pas rempli.",
        default=False,
        missing=False,
    )


def accounting_exporter_choices_query() -> Iterable[User]:
    from caerp.models.export.accounting_export_log import AccountingExportLogEntry

    query = AccountingExportLogEntry.query()
    query = query.join(AccountingExportLogEntry.user)
    query = query.with_entities(User)
    query = query.distinct()
    return query


@colander.deferred
def deferred_accounting_exporter_choice(node, kw):
    return deform.widget.SelectWidget(
        values=[("", "Tous")]
        + [(str(i.id), i.label) for i in accounting_exporter_choices_query()]
    )


@colander.deferred
def deferred_export_type_choice(node, kw):
    # deferred mostly to avoid circular import…
    from caerp.views.export.utils import (
        format_export_type,
        ACCOUNTING_EXPORT_TYPE_OPTIONS,
    )

    choices = [("", "Tous")] + [
        (i, format_export_type(i)) for i in ACCOUNTING_EXPORT_TYPE_OPTIONS
    ]
    return deform.widget.SelectWidget(values=choices)


class AccountingExportLogEntryListSchema(BaseListsSchema):
    _common_kwargs = dict(
        missing=colander.drop,
        insert_before="items_per_page",
    )

    start_date = colander.SchemaNode(
        colander.Date(),
        title="Exporté entre le",
        **_common_kwargs,
    )
    end_date = colander.SchemaNode(
        colander.Date(),
        title="et le",
        **_common_kwargs,
    )
    user_id = colander.SchemaNode(
        colander.Integer(),
        title="Exporté par",
        widget=deferred_accounting_exporter_choice,
        **_common_kwargs,
    )
    export_type = colander.SchemaNode(
        colander.String(),
        title="Type d'export",
        widget=deferred_export_type_choice,
        **_common_kwargs,
    )

    def validator(self, form, value):
        if value.get("start_date") and value.get("end_date"):
            if value["start_date"] > value["end_date"]:
                exc = colander.Invalid(
                    form, "La date de début doit précéder la date de fin"
                )
                exc["start_date"] = "Doit précéder la date de fin"
                raise exc


def get_accounting_export_log_schema():
    schema = AccountingExportLogEntryListSchema()
    del schema["search"]
    return schema

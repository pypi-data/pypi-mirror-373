import logging

from zope.interface import implementer

from caerp.interfaces import ITreasuryProducer

from .base import MissingData, double_lines, filter_accounting_entry
from .expense import BaseSageExpenseContribution

logger = log = logging.getLogger(__name__)


class SageSupplierInvoice:
    def __init__(self, supplier_invoice, config=None):
        self.lines = []
        self.supplier_invoice = supplier_invoice
        self.company = supplier_invoice.company
        self.supplier = supplier_invoice.supplier
        self.config = config or {}
        self.grouped = self.is_grouped()

    def is_grouped(self):
        logger.debug(self.config.get("ungroup_supplier_invoices_export"))
        return not self.config.get("ungroup_supplier_invoices_export", "0") == "1"

    def populate(self):
        self.lines = []
        if self.grouped:
            for charge_group in self.supplier_invoice.get_lines_by_type():
                expense_type = charge_group[0].expense_type
                if expense_type is None:
                    raise MissingData("Supplier invoice line is missing expense type")
                ht = sum([line.total_ht for line in charge_group])
                tva = sum([line.total_tva for line in charge_group])

                self.lines.append(
                    {
                        "expense_type": expense_type,
                        "ht": ht,
                        "tva": tva,
                        "ttc": 0,  # la ligne de credit est sur le total global
                    }
                )
        else:
            for line in self.supplier_invoice.lines:
                ht = line.total_ht
                self.lines.append(
                    {
                        "expense_type": line.expense_type,
                        "ht": ht,
                        "tva": line.total_tva,
                        "description": line.description,
                        "ttc": line.total,
                        "cae_total": line.cae_total,
                        "worker_total": line.worker_total,
                    }
                )


class SageSupplierInvoiceBase(BaseSageExpenseContribution):
    static_columns = (
        "code_journal",
        "date",
        "type_",
        "num_caerp",
        "supplier_label",
        "company_name",
        "user_name",
        "num_analytique",
        "remote_invoice_number",
    )
    variable_columns = (
        "compte_cg",
        "compte_tiers",
        "code_tva",
        "debit",
        "credit",
        # Est overrider dans certaines écritures donc variable
        "libelle",
    )

    _label_template_key = "bookentry_supplier_invoice_label_template"

    def set_supplier_invoice(self, wrapped_supplier_invoice):
        self.wrapped_invoice = wrapped_supplier_invoice
        self.supplier_invoice = wrapped_supplier_invoice.supplier_invoice
        self.company = wrapped_supplier_invoice.company
        self.supplier = wrapped_supplier_invoice.supplier
        self.user = self.supplier_invoice.payer

    @property
    def code_journal(self):
        return self._get_config_value("code_journal_frns")

    @property
    def date(self):
        if self.supplier_invoice.date:
            return self.supplier_invoice.date
        else:
            return ""

    @property
    def num_caerp(self):
        return str(self.supplier_invoice.official_number)

    @property
    def remote_invoice_number(self):
        return self.supplier_invoice.remote_invoice_number or ""

    @property
    def supplier_label(self):
        return self.supplier.label

    @property
    def company_name(self):
        return self.company.name

    @property
    def user_name(self):
        if not self.user:
            return ""
        return self.user.label

    @property
    def num_analytique(self):
        return self.company.code_compta


class SageSupplierInvoiceMain(SageSupplierInvoiceBase):
    """
    Main module for supplier_invoice export to sage.

    Exports :

    - supplier product lines
    - contribution lines

    Lines can be grouped by expense type if the
    ungroup_supplier_invoices_export is not checked
    """

    def _credit_all(self, cae_ttc, worker_ttc, line_libelle):
        if self.supplier_invoice.cae_percentage > 0:
            yield self._credit_supplier(cae_ttc, line_libelle)
        if self.supplier_invoice.cae_percentage < 100:
            yield self._credit_worker(worker_ttc, line_libelle)

    @double_lines
    def _credit_supplier(self, ttc, line_libelle):
        """
        Main CREDIT The mainline for our supplier invoice: supplier part
        """
        entry = self.get_base_entry()
        entry.update(
            compte_cg=self.supplier.get_general_account(prefix=self.config_key_prefix),
            compte_tiers=self.supplier.get_third_party_account(
                prefix=self.config_key_prefix
            ),
            credit=ttc,
            libelle=line_libelle,
        )
        return entry

    @double_lines
    def _credit_worker(self, ttc, line_libelle):
        """
        Main CREDIT The mainline for our supplier invoice : worker part
        """
        entry = self.get_base_entry()
        entry.update(
            compte_cg=self.company.get_general_expense_account(),
            compte_tiers=self.user.compte_tiers,
            credit=ttc,
            libelle=line_libelle,
        )
        return entry

    @double_lines
    def _debit_ht(self, expense_type, ht, line_libelle):
        """
        Débit HT du total de la charge
        """
        entry = self.get_base_entry()
        entry.update(
            compte_cg=expense_type.code,
            code_tva=expense_type.code_tva,
            debit=ht,
            libelle=line_libelle,
        )
        return entry

    @double_lines
    def _debit_tva(self, expense_type, tva, line_libelle):
        """
        Débit TVA de la charge
        """
        if expense_type.compte_tva is None:
            raise MissingData("Sage Expense : Missing compte_tva in expense_type")
        entry = self.get_base_entry()
        entry.update(
            compte_cg=expense_type.compte_tva,
            code_tva=expense_type.code_tva,
            debit=tva,
            libelle=line_libelle,
        )
        return entry

    @double_lines
    def _credit_tva_on_margin(self, expense_type, tva, line_libelle):
        # Alternative to _debit_tva() when in tva on margin mode for a line
        if expense_type.compte_tva is None:
            raise MissingData(
                "Sage Expense : Missing compte_produit_tva_on_margin          "
                "      in expense_type"
            )

        entry = self.get_base_entry()
        entry.update(
            compte_cg=expense_type.compte_produit_tva_on_margin,
            code_tva=expense_type.code_tva,
            credit=tva,
            libelle=line_libelle,
        )
        return entry

    def _libelle(self, description):
        return (
            self.label_template.format(
                company=self.company,
                supplier=self.supplier,
                line_description=description,
                supplier_invoice=self.supplier_invoice,
            )
            .replace("None", "")
            .strip()
        )

    def yield_entries(self):
        """
        Yield all the book entries for the current supplier invoice
        """
        total = self.supplier_invoice.total
        cae_total = self.supplier_invoice.cae_total
        worker_total = self.supplier_invoice.worker_total

        grouped_by_type = self.wrapped_invoice.grouped

        if total != 0:
            default_libelle = self._libelle("")
            if grouped_by_type:
                logger.debug("The data are grouped")

                yield from self._credit_all(cae_total, worker_total, default_libelle)

            for line in self.wrapped_invoice.lines:
                logger.debug("Line {}".format(line))
                expense_type = line["expense_type"]
                ht = line["ht"]
                tva = line["tva"]
                if not grouped_by_type:
                    libelle = self._libelle(line["description"])
                    yield from self._credit_all(
                        line["cae_total"],
                        line["worker_total"],
                        libelle,
                    )
                else:
                    libelle = default_libelle

                if ht != 0:
                    if expense_type.tva_on_margin:
                        yield self._debit_ht(expense_type, ht + tva, libelle)
                    else:
                        yield self._debit_ht(expense_type, ht, libelle)
                if tva != 0:
                    if expense_type.tva_on_margin:
                        yield self._credit_tva_on_margin(expense_type, tva, libelle)
                    yield self._debit_tva(expense_type, tva, libelle)

                if expense_type.contribution and self._has_contribution_module():
                    # Method inherited from BaseSageExpenseContribution
                    yield from self.yield_contribution_entries(
                        ht, libelle=default_libelle
                    )
        else:
            log.warn(
                "Exporting a void supplier invoice : {0}".format(
                    self.supplier_invoice.id
                )
            )


class InternalSageSupplierInvoiceMain(SageSupplierInvoiceMain):
    config_key_prefix = "internal"


@implementer(ITreasuryProducer)
class SupplierInvoiceExportProducer:
    """
    Export a supplier invoice to Sage
    """

    _default_modules = (SageSupplierInvoiceMain,)
    use_analytic = True
    use_general = True

    def __init__(self, context, request):
        self.request = request
        self.config = request.config
        self.modules = []
        for module in self._default_modules:
            self.modules.append(module(context, request))

    def _get_item_book_entries(self, supplier_invoice):
        """
        Return book entries for a single supplier_invoice
        """
        wrapped_invoice = SageSupplierInvoice(supplier_invoice, self.config)
        wrapped_invoice.populate()
        for module in self.modules:
            module.set_supplier_invoice(wrapped_invoice)
            for entry in module.yield_entries():
                gen_line, analytic_line = entry
                if self.use_general:
                    yield filter_accounting_entry(gen_line)
                if self.use_analytic:
                    yield filter_accounting_entry(analytic_line)

    def get_item_book_entries(self, supplier_invoice):
        return list(self._get_item_book_entries(supplier_invoice))

    def get_book_entries(self, supplier_invoices):
        """
        Return the book entries for an supplier_invoicelist
        """
        result = []
        for supplier_invoice in supplier_invoices:
            result.extend(list(self._get_item_book_entries(supplier_invoice)))
        return result


class InternalSupplierInvoiceExportProducer(SupplierInvoiceExportProducer):
    config_key_prefix = "internal"
    _default_modules = (InternalSageSupplierInvoiceMain,)

import logging
import datetime

from zope.interface import implementer

from caerp.interfaces import (
    ITreasuryGroupper,
    ITreasuryProducer,
)
from caerp.models.config import Config
from caerp.models.tva import Tva
from caerp.models.accounting.bookeeping import CustomInvoiceBookEntryModule
from caerp.compute.math_utils import (
    floor_to_precision,
    percentage,
)
from caerp.utils.accounting import get_customer_accounting_general_account
from caerp.utils.compat import Iterable
from caerp.utils.strings import strip_civilite

from .base import (
    MissingData,
    double_lines,
    BaseSageBookEntryFactory,
    filter_accounting_entry,
)

logger = log = logging.getLogger(__name__)


class SageInvoice:
    """
    Sage wrapper for invoices
    1- Peupler les produits
        * Un produit doit avoir:
            * TVA
            * HT
            * Compte CG Produit
            * Compte CG TVA
            * (Code TVA)

    Pour chaque ligne :
        créer produit ou ajouter au produit existant

    Pour chaque ligne de remise:
        créer produit ou ajouter au produit existant

    Si dépense HT ou dépense TTC:
        créer produit
    """

    expense_tva_compte_cg = None
    expense_tva_code = None

    def __init__(self, invoice, config=None, default_tva=None):
        self.products = {}
        self.invoice = invoice
        self.config = config or {}
        self.default_tva = default_tva or Tva.get_default()
        self.tvas = self.invoice.get_tvas_by_product()

    def _get_config_value(self, key, default=None):
        if self.invoice.internal:
            key = "internal{}".format(key)
        return self.config.get(key, default)

    def get_product(
        self, key, compte_cg_produit, compte_cg_tva, code_tva, tva_val, tva_id=None
    ):
        """
        Return the product dict belonging to the key "compte_cg_produit"
        """
        return self.products.setdefault(
            key,
            {
                "compte_cg_produit": compte_cg_produit,
                "compte_cg_tva": compte_cg_tva,
                "code_tva": code_tva,
                "tva": tva_val,
                "tva_id": tva_id,
            },
        )

    def _populate_invoice_lines(self):
        """
        populate the object with the content of our lines
        """
        for line in self.invoice.all_lines:
            product_model = line.product
            if product_model is None:
                raise MissingData("No product found for this invoice line")
            compte_cg_produit = line.product.compte_cg
            compte_cg_tva = line.product.tva.compte_cg
            key = (compte_cg_produit, compte_cg_tva)
            prod = self.get_product(
                key,
                compte_cg_produit,
                compte_cg_tva,
                line.product.tva.code,
                self.tvas.get(key, 0),
                line.product.tva.id,
            )
            prod["ht"] = prod.get("ht", 0) + line.total_ht()

    def _populate_discounts(self):
        """
        populate our object with the content of discount lines
        discount lines are grouped in a unique book entry, the TVA used is
        specific to the RRR, no book entry is returned if the code and
        compte cg for this specific book entry type is defined
        """
        compte_cg_tva = self._get_config_value("compte_cg_tva_rrr", "")
        code_tva = self._get_config_value("code_tva_rrr", "")
        compte_rrr = self._get_config_value("compte_rrr")

        if self.invoice.discounts:
            for line in self.invoice.discounts:
                if self.invoice.internal:
                    if line.tva > 0:
                        tva = Tva.by_value(line.tva)
                        compte_cg_tva = tva.compte_cg
                        code_tva = tva.code
                        tva_id = tva.id
                    else:
                        compte_cg_tva = ""
                        code_tva = ""
                        tva_id = None

                if not compte_rrr:
                    raise MissingData(
                        "Missing RRR configuration : compte_rrr='{}'".format(compte_rrr)
                    )
                elif line.tva > 0 and not compte_cg_tva:
                    raise MissingData(
                        "Missing RRR configuration : tva={}, compte_cg_tva='{}',"
                        " code_tva='{}'".format(line.tva, compte_cg_tva, code_tva)
                    )
                else:
                    tva_val = self.tvas.get("rrr", 0)
                    prod = self.get_product(
                        "rrr",
                        compte_rrr,
                        compte_cg_tva,
                        code_tva,
                        tva_val,
                    )
                    prod["ht"] = prod.get("ht", 0) + line.total_ht()
                    tva = Tva.by_value(line.tva)
                    if tva:
                        prod["tva_id"] = tva.id

    def _populate_expenses(self):
        """
        Add the expenses to our object
        """
        if self.invoice.expenses > 0 or self.invoice.expenses_ht > 0:
            if self.expense_tva_compte_cg is None:
                self.expense_tva_compte_cg = self.default_tva.compte_cg
                self.expense_tva_code = self.default_tva.code

            compte_cg = self._get_config_value("compte_frais_annexes")
            tva_val = self.tvas.get("expense", 0)
            key = (compte_cg, self.expense_tva_compte_cg)
            prod = self.get_product(
                key,
                compte_cg,
                self.expense_tva_compte_cg,
                self.expense_tva_code,
                tva_val,
            )
            ht_expense = self.invoice.get_expense_ht()
            ttc_expense = self.invoice.expenses_amount()
            prod["ht"] = ttc_expense + ht_expense.total_ht()
            tva = Tva.by_value(self.invoice.get_expenses_tva())
            if tva:
                prod["tva_id"] = tva.id

    def _round_products(self):
        """
        Round the products ht and tva
        """
        for value in list(self.products.values()):
            value["ht"] = floor_to_precision(value["ht"])
            value["tva"] = floor_to_precision(value["tva"])

    def populate(self):
        """
        populate the products entries with the current invoice
        """
        self._populate_invoice_lines()
        self._populate_discounts()
        self._populate_expenses()
        self._round_products()


class BaseInvoiceBookEntryFactory(BaseSageBookEntryFactory):
    """
    Base Sage Export module
    """

    static_columns = (
        "code_journal",
        "date",
        "num_caerp",
        "libelle",
        "type_",
        "customer_label",
        "company_name",
        "task_name",
    )
    variable_columns = (
        "compte_cg",
        "num_analytique",
        "compte_tiers",
        "code_tva",
        "echeance",
        "debit",
        "credit",
    )

    @staticmethod
    def _amount_method(a, b):
        return percentage(a, b)

    def set_invoice(self, wrapped_invoice):
        """
        Set the current invoice to process
        """
        self.wrapped_invoice = wrapped_invoice
        self.invoice = wrapped_invoice.invoice
        self.company = self.invoice.company
        self.customer = self.invoice.customer

    @property
    def code_journal(self):
        """
        Return the code of the destination journal from the treasury book
        """
        return self._get_config_value("code_journal")

    @property
    def date(self):
        """
        Return the date field
        """
        return self.invoice.date

    @property
    def num_caerp(self):
        """
        Return the invoice number
        """
        return self.invoice.official_number

    @property
    def libelle(self):
        """
        Return the label for our book entry
        """
        try:
            return strip_civilite(
                self.label_template.format(
                    company=self.company,
                    invoice=self.invoice,
                    # backward compatibility
                    client=self.customer,
                    # backward compatibility:
                    num_caerp=self.invoice.official_number,
                    # backward compatibility:
                    numero_facture=self.invoice.official_number,
                    # backward compatibility:
                    entreprise=self.company,
                )
                .replace("None", "")
                .strip()
            )
        except AttributeError:
            raise NotImplementedError(
                "The class {} should define a {} attribute.".format(
                    self.__class__,
                    self.label_template,
                )
            )

    @property
    def customer_label(self):
        return strip_civilite(self.customer.label)

    @property
    def company_name(self):
        return self.company.name

    @property
    def task_name(self):
        return self.invoice.name


class SageFacturation(BaseInvoiceBookEntryFactory):
    """
        Facturation treasury export module
        implements IMainInvoiceTreasury

        For each product exports exportsthree types of treasury lines
            * Crédit TotalHT
            * Crédit TVA
            * Débit TTC

        Expenses and discounts are also exported

        Uses :
            Numéro analytique de l'enseigne
            Compte CG produit
            Compte CG TVA
            Compte CG de l'enseigne
            Compte Tiers du client
            Code TVA

            Compte CG Annexe
            Compte CG RRR

        Columns :
            * Num facture
            * Date
            * Compte CG
            * Numéro analytique
            * Compte Tiers
            * Code TVA
            * Date d'échéance
            * Libellés
            * Montant

    Works together with InvoiceExportGroupper for line grouping
    """

    _label_template_key = "bookentry_facturation_label_template"

    @property
    def num_analytique(self):
        """
        Return the analytic number common to all entries in the current
        export module
        """
        return self.company.code_compta

    @double_lines
    def credit_totalht(self, product):
        """
        Return a Credit Total HT entry
        """
        entry = self.get_base_entry()
        entry.update(
            compte_cg=product["compte_cg_produit"],
            num_analytique=self.num_analytique,
            code_tva=product["code_tva"],
        )

        # Hack to handle discount lines inversion
        compte_rrr = self._get_config_value("compte_rrr")
        if product["compte_cg_produit"] == compte_rrr:
            entry["debit"] = product["ht"]
        else:
            entry["credit"] = product["ht"]

        return entry

    @double_lines
    def credit_tva(self, product):
        """
        Return a Credit TVA entry
        """
        entry = self.get_base_entry()
        entry.update(
            compte_cg=product["compte_cg_tva"],
            num_analytique=self.num_analytique,
            code_tva=product["code_tva"],
        )

        compte_rrr = self._get_config_value("compte_rrr")
        if product["compte_cg_produit"] == compte_rrr:
            entry["debit"] = product["tva"]
        else:
            entry["credit"] = product["tva"]

        return entry

    @double_lines
    def debit_ttc(self, product):
        """
        Return a debit TTC entry
        """
        entry = self.get_base_entry()
        echeance = self.invoice.date + datetime.timedelta(days=30)
        customer_general_account = get_customer_accounting_general_account(
            self.request, self.customer.id, product["tva_id"], self.config_key_prefix
        )
        entry.update(
            compte_cg=customer_general_account,
            num_analytique=self.num_analytique,
            compte_tiers=self.customer.get_third_party_account(self.config_key_prefix),
            echeance=echeance,
            _mark_customer_debit=True,  # for InvoiceExportGroupper
            _tva_id=product["tva_id"],  # for InvoiceExportGroupper
        )

        compte_rrr = self._get_config_value("compte_rrr")
        if product["compte_cg_produit"] == compte_rrr:
            entry["credit"] = product["ht"] + product["tva"]
        else:
            entry["debit"] = product["ht"] + product["tva"]

        return entry

    @staticmethod
    def _has_tva_value(product):
        """
        Test whether the tva of the given product has a positive value
        """
        return product["tva"] != 0

    def yield_entries(self):
        """
        Produce all the entries for the current task
        """
        for product in list(self.wrapped_invoice.products.values()):
            yield self.credit_totalht(product)
            if self._has_tva_value(product):
                yield self.credit_tva(product)
            yield self.debit_ttc(product)


class InternalSageFacturation(SageFacturation):
    config_key_prefix = "internal"

    def _has_tva_value(self, *args, **kwargs):
        return False


class SageRGInterne(BaseInvoiceBookEntryFactory):
    """
    The RGINterne module
    """

    _part_key = "taux_rg_interne"
    _label_template_key = "bookentry_rg_interne_label_template"

    def get_amount(self, product):
        """
        Return the amount for the current module
        (the same for credit or debit)
        """
        ttc = product["ht"] + product["tva"]
        return self._amount_method(ttc, self.get_part())

    @double_lines
    def debit_company(self, product):
        """
        Debit entreprise book entry
        """
        entry = self.get_base_entry()
        entry.update(
            compte_cg=self._get_config_value("compte_rg_interne"),
            num_analytique=self.company.code_compta,
            debit=self.get_amount(product),
        )
        return entry

    @double_lines
    def credit_company(self, product):
        """
        Credit entreprise book entry
        """
        entry = self.get_base_entry()
        entry.update(
            compte_cg=self._get_config_value("compte_cg_banque"),
            num_analytique=self.company.code_compta,
            credit=self.get_amount(product),
        )
        return entry

    @double_lines
    def debit_cae(self, product):
        """
        Debit cae book entry
        """
        entry = self.get_base_entry()
        entry.update(
            compte_cg=self._get_config_value("compte_cg_banque"),
            num_analytique=self._get_config_value("numero_analytique"),
            debit=self.get_amount(product),
        )
        return entry

    @double_lines
    def credit_cae(self, product):
        """
        Credit CAE book entry
        """
        entry = self.get_base_entry()
        entry.update(
            compte_cg=self._get_config_value("compte_rg_interne"),
            num_analytique=self._get_config_value("numero_analytique"),
            credit=self.get_amount(product),
        )
        return entry

    def yield_entries(self):
        """
        yield book entries
        """
        for product in list(self.wrapped_invoice.products.values()):
            yield self.debit_company(product)
            yield self.credit_company(product)
            yield self.debit_cae(product)
            yield self.credit_cae(product)


class SageRGClient(BaseInvoiceBookEntryFactory):
    """
    The Rg client module
    """

    _part_key = "taux_rg_client"
    _label_template_key = "bookentry_rg_client_label_template"

    def get_amount(self, product):
        """
        Return the amount for the current module
        (the same for credit or debit)
        """
        ttc = product["ht"] + product["tva"]
        return self._amount_method(ttc, self.get_part())

    def get_echeance(self):
        """
        Return the value for the "echeance" column now + 365 days
        """
        echeance = self.invoice.date + datetime.timedelta(days=365)
        return echeance

    @double_lines
    def debit_company(self, product):
        """
        Debit entreprise book entry
        """
        entry = self.get_base_entry()
        entry.update(
            compte_cg=self._get_config_value("compte_rg_externe"),
            num_analytique=self.company.code_compta,
            debit=self.get_amount(product),
            echeance=self.get_echeance(),
        )
        return entry

    @double_lines
    def credit_company(self, product):
        """
        Credit entreprise book entry
        """
        entry = self.get_base_entry()
        customer_general_account = get_customer_accounting_general_account(
            self.request, self.customer.id, product["tva_id"]
        )
        entry.update(
            compte_cg=customer_general_account,
            num_analytique=self.company.code_compta,
            credit=self.get_amount(product),
            compte_tiers=self.customer.get_third_party_account(),
            echeance=self.get_echeance(),
        )
        return entry

    def yield_entries(self):
        """
        yield book entries
        """
        for product in list(self.wrapped_invoice.products.values()):
            yield self.debit_company(product)
            yield self.credit_company(product)


class CustomBookEntryFactory(BaseInvoiceBookEntryFactory):
    """
    A custom book entry module used to produce entries
    """

    def __init__(self, context, request, module_config):
        BaseInvoiceBookEntryFactory.__init__(self, context, request)
        self.cg_debit = module_config.compte_cg_debit  # compte de charge
        self.cg_credit = module_config.compte_cg_credit  # compte de contrepartie
        self.cg_banque = self._get_config_value("compte_cg_banque")
        self.analytique_cae = self._get_config_value("numero_analytique")
        self.label_template = module_config.label_template
        self.percentage = module_config.percentage
        self.name = module_config.name
        self.is_provision = module_config.is_provision

    def get_part(self):
        """
        Collect the percentage to apply on this custom module
        """
        # Si le CustomInvoiceBookEntry a un name, c'est qu'il peut être
        # personnalisé au travers de l'application (niveau enseigne ou
        # niveau document)
        if self.name:
            rate = self.invoice.get_rate(self.name)
        else:
            rate = self.percentage
        return rate

    def get_amount(self):
        """
        Return the amount for the current module
        (the same for credit or debit)
        """
        return self._amount_method(self.invoice.total_ht(), self.get_part())

    @double_lines
    def debit_company(self):
        """
        Debit entreprise book entry
        """
        entry = self.get_base_entry()
        entry.update(
            compte_cg=self.cg_debit,
            num_analytique=self.company.code_compta,
            debit=self.get_amount(),
        )
        return entry

    @double_lines
    def credit_company(self):
        """
        Credit entreprise book entry
        """
        if self.is_provision:
            cg_credit_company = self.cg_credit
        else:
            cg_credit_company = self.cg_banque
        entry = self.get_base_entry()
        entry.update(
            compte_cg=cg_credit_company,
            num_analytique=self.company.code_compta,
            credit=self.get_amount(),
        )
        return entry

    @double_lines
    def debit_cae(self):
        """
        Debit cae book entry
        """
        entry = self.get_base_entry()
        entry.update(
            compte_cg=self.cg_banque,
            num_analytique=self.analytique_cae,
            debit=self.get_amount(),
        )
        return entry

    @double_lines
    def credit_cae(self):
        """
        Credit CAE book entry
        """
        entry = self.get_base_entry()
        entry.update(
            compte_cg=self.cg_credit,
            num_analytique=self.analytique_cae,
            credit=self.get_amount(),
        )
        return entry

    def yield_entries(self):
        """
        yield book entries
        """
        yield self.debit_company()
        yield self.credit_company()
        if not self.is_provision:
            yield self.debit_cae()
            yield self.credit_cae()


class InternalCustomBookEntryFactory(CustomBookEntryFactory):
    config_key_prefix = "internal"


@implementer(ITreasuryProducer)
class InvoiceExportProducer:
    """
    base module for treasury export @param config: application
    configuration dict, contains all the CAE wide
    account configurations
    """

    use_general = True
    use_analytic = True
    _default_modules = (SageFacturation,)
    _available_modules = {
        "sage_rginterne": SageRGInterne,
        "sage_rgclient": SageRGClient,
    }
    _custom_factory = CustomBookEntryFactory

    def __init__(self, context, request):
        self.request = request
        self.config = request.config
        self.modules = []
        for module in self._default_modules:
            self.modules.append(module(context, request))

        for config_key, module in list(self._available_modules.items()):
            if self.config.get(config_key) == "1":
                logger.debug("  + Module {} is enabled".format(module))
                self.modules.append(module(context, request))

        if self._custom_factory is not None and hasattr(request, "dbsession"):
            self._load_custom_modules(context, request)

    def _load_custom_modules(self, context, request):
        """
        Load custom modules configuration and initialize them
        """
        query = CustomInvoiceBookEntryModule.query()
        query = query.filter_by(doctype="invoice")
        for module in query.filter_by(enabled=True):
            self.modules.append(
                self._custom_factory(
                    context,
                    request,
                    module,
                )
            )

    def _get_item_book_entries(self, invoice):
        """
        Yield the book entries for a given invoice
        """
        # We wrap the invoice with some common computing tools
        wrapped_invoice = SageInvoice(invoice, self.config)
        wrapped_invoice.populate()
        for module in self.modules:
            module.set_invoice(wrapped_invoice)
            for entry in module.yield_entries():
                gen_line, analytic_line = entry
                if self.use_general:
                    yield filter_accounting_entry(gen_line)
                if self.use_analytic:
                    yield filter_accounting_entry(analytic_line)

    def get_item_book_entries(self, invoice):
        """
        Return book entries for a single invoice

        :param obj invoice: Invoice/CancelInvoice object
        :returns: List of invoice book entries as lines of values
        :rtype: list
        """
        return list(self._get_item_book_entries(invoice))

    def get_book_entries(self, invoicelist):
        """
        Return the book entries for a list of invoices
        """
        result = []
        for invoice in invoicelist:
            result.extend(list(self._get_item_book_entries(invoice)))
        return result


class InternalInvoiceExportProducer(InvoiceExportProducer):
    _default_modules = (InternalSageFacturation,)
    _custom_factory = InternalCustomBookEntryFactory
    _available_modules = {}

    def _load_custom_modules(self, context, request):
        """
        Load custom modules configuration and initialize them
        """
        query = CustomInvoiceBookEntryModule.query()
        query = query.filter_by(doctype="internalinvoice")
        for module in query.filter_by(enabled=True):
            self.modules.append(self._custom_factory(context, request, module))


@implementer(ITreasuryGroupper)
class InvoiceExportGroupper:
    """
    Group export lines of an invoice

    This groupper must be applied only to the lines of a single invoice at once.

    Can do the following grouping


    # Group customer (typically 411*) lines of an invoice into one

    This grouping is toggled by this setting :

      * bookentry_sales_group_customer_entries config setting.

    It relies on following fields on line item:

      * _mark_customer_debit=True
      * _tva_id
      * num_caerp

    """

    def __init__(self):
        self._group_customer_lines = Config.get_value(
            "bookentry_sales_group_customer_entries",
            type_=bool,
        )
        self._customer_account_by_tva = Config.get_value(
            "bookentry_sales_customer_account_by_tva",
            type_=bool,
        )

    def group_into(self, group_item: dict, member_item: dict) -> None:
        # we should not be handling in same grouper lines from different invoices
        assert member_item["num_caerp"] == group_item["num_caerp"]

        # merge item2 into item1 (inplace).
        # credit may be needed for RRR
        # We do not want to have both credit and debit for a same line
        summed_debit = (
            (group_item.get("debit") or 0) + (member_item.get("debit") or 0)
        ) - ((group_item.get("credit") or 0) + (member_item.get("credit") or 0))
        if summed_debit > 0:
            # Total > 0 after applying RRR
            group_item["debit"], group_item["credit"] = summed_debit, 0
        else:
            # Total < 0 after applying RRR
            group_item["debit"], group_item["credit"] = 0, -summed_debit

    def group_items(self, items: Iterable[dict]) -> Iterable[dict]:
        if not self._group_customer_lines:
            # no-op
            groupped_lines = items

        else:
            groupped_lines = []
            customer_single_lines = {}

            for item in items:
                if item.get("_mark_customer_debit", False):
                    tva_id = item.get("_tva_id", None)
                    line_type = item["type_"]  # A / G
                    if self._customer_account_by_tva:
                        _group_key = (line_type, tva_id)
                    else:
                        _group_key = line_type
                    customer_single_line = customer_single_lines.get(_group_key)
                    if customer_single_line:
                        self.group_into(customer_single_line, item)
                    else:
                        customer_single_line = item.copy()
                        customer_single_lines[_group_key] = customer_single_line
                        groupped_lines.append(customer_single_line)
                else:
                    # Lines that are not relevant for grouping
                    groupped_lines.append(item)

        return groupped_lines

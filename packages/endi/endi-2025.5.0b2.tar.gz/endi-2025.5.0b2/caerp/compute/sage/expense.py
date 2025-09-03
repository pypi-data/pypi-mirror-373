import logging
import datetime

from zope.interface import implementer

from caerp.interfaces import ITreasuryProducer
from caerp.models.expense import ExpenseSheet
from caerp.models.expense.sheet import BaseExpenseLine
from caerp.compute.math_utils import percentage
from caerp.utils.strings import format_account
from .base import (
    MissingData,
    double_lines,
    BaseSageBookEntryFactory,
    filter_accounting_entry,
)

logger = log = logging.getLogger(__name__)


class BaseSageExpenseContribution(BaseSageBookEntryFactory):
    """
    Base contribution line generator used for expenses
    """

    def __init__(self, *args, **kwargs):
        BaseSageBookEntryFactory.__init__(self, *args, **kwargs)
        self.contribution_module = self.get_contribution_module()
        self.category: str = ""

    def _has_contribution_module(self):
        return bool(self.contribution_module)

    def _get_contribution_amount(self, ht):
        """
        Return the contribution on the HT total
        """
        return percentage(ht, self.get_contribution())

    @double_lines
    def _credit_company(self, value, **kwargs):
        """
        Contribution : Crédit entreprise
        """
        entry = self.get_base_entry()

        entry.update(
            compte_cg=self.contribution_module.compte_cg_debit,
            num_analytique=self.company.code_compta,
            credit=value,
            **kwargs,
        )
        return entry

    @double_lines
    def _debit_company(self, value, **kwargs):
        """
        Contribution : Débit entreprise
        """
        entry = self.get_base_entry()
        entry.update(
            compte_cg=self._get_config_value("compte_cg_banque"),
            num_analytique=self.company.code_compta,
            debit=value,
            **kwargs,
        )
        return entry

    @double_lines
    def _credit_cae(self, value, **kwargs):
        """
        Contribution : Crédit CAE
        """
        entry = self.get_base_entry()
        entry.update(
            compte_cg=self._get_config_value("compte_cg_banque"),
            num_analytique=self._get_config_value("numero_analytique"),
            credit=value,
            **kwargs,
        )
        return entry

    @double_lines
    def _debit_cae(self, value, **kwargs):
        """
        Contribution : Débit CAE
        """
        entry = self.get_base_entry()
        entry.update(
            compte_cg=self.contribution_module.compte_cg_credit,
            num_analytique=self._get_config_value("numero_analytique"),
            debit=value,
            **kwargs,
        )
        return entry

    def yield_contribution_entries(self, amount, **kwargs):
        contribution = self._get_contribution_amount(amount)

        if not kwargs.get("date"):
            kwargs.pop("date", None)

        yield self._credit_company(contribution, **kwargs)
        yield self._debit_company(contribution, **kwargs)
        yield self._credit_cae(contribution, **kwargs)
        yield self._debit_cae(contribution, **kwargs)


class SageExpenseBase(BaseSageExpenseContribution):
    static_columns = (
        "code_journal",
        "num_feuille",
        "type_",
        "num_caerp",
        "num_analytique",
        "user_name",
        "company_name",
    )
    variable_columns = (
        "compte_cg",
        "compte_tiers",
        "code_tva",
        "debit",
        "credit",
        "libelle",
        "date",
    )

    _label_template_key = "bookentry_expense_label_template"

    def set_expense(self, expense: ExpenseSheet):
        self.expense = expense
        self.company = expense.company

    @property
    def code_journal(self):
        return self.config["code_journal_ndf"]

    @property
    def date(self):
        expense_date = datetime.date(self.expense.year, self.expense.month, 1)
        return expense_date

    @property
    def num_feuille(self):
        return "ndf{0}{1}".format(self.expense.month, self.expense.year)

    @property
    def num_caerp(self):
        return str(self.expense.official_number)

    @property
    def libelle(self):
        return self._mk_libelle(self.expense, None)

    @property
    def num_analytique(self):
        return self.company.code_compta

    @property
    def user_name(self):
        return self.expense.user.label

    @property
    def company_name(self):
        return self.company.name

    def get_line_libelle(self, expenseline: "BaseExpenseLine") -> str:
        """Libelle, but for ungroupped exports"""
        # ExpenseKmLine.supplier does not exist
        supplier = getattr(expenseline, "supplier", None)
        # Same for invoice_number
        invoice_number = getattr(expenseline, "invoice_number", None)
        return self._mk_libelle(
            self.expense,
            supplier,
            expenseline.description,
            invoice_number,
        )

    def _mk_libelle(self, sheet, supplier, description="", invoice_number="") -> str:
        # Expose `supplier_name` rather than `supplier` (as on suppplier
        # invoices) because it could crash (supplier is not mandatory for
        # ExpenseLine, and not even present on ExpenseKmLine.
        return (
            self.label_template.format(
                beneficiaire=format_account(sheet.user, reverse=False),
                beneficiaire_LASTNAME=sheet.user.lastname.upper(),
                code_compta=sheet.company.code_compta,
                expense=sheet,
                expense_date=datetime.date(sheet.year, sheet.month, 1),
                expense_description=description,
                invoice_number=invoice_number,
                supplier_label=supplier.label if supplier else "",
                titre=sheet.title if sheet.title else "",
            )
            .replace("None", "")
            .strip()
        )


class SageExpenseMain(SageExpenseBase):
    """
    Main module for expense export to sage.
    Should be the only module, but we keep more or less the same structure as
    for invoice exports
    """

    def set_category(self, category):
        self.category = category

    @double_lines
    def _credit(self, ht, **kwargs):
        """
        Main CREDIT The mainline for our expense sheet
        """
        entry = self.get_base_entry()
        entry.update(
            compte_cg=self.company.get_general_expense_account(),
            compte_tiers=self.expense.user.compte_tiers,
            credit=ht,
            **kwargs,
        )
        return entry

    @double_lines
    def _debit_ht(self, expense_type, ht, **kwargs):
        """
        Débit HT du total de la charge
        """
        entry = self.get_base_entry()
        entry.update(
            compte_cg=expense_type.code,
            code_tva=expense_type.code_tva,
            debit=ht,
            **kwargs,
        )
        return entry

    @double_lines
    def _credit_tva_on_margin(self, expense_type, tva, **kwargs):
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
            **kwargs,
        )
        return entry

    @double_lines
    def _debit_tva(self, expense_type, tva, **kwargs):
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
            **kwargs,
        )
        return entry

    def _write_complete_debit(self, expense_type, ht, tva, **kwargs):
        """
        Write a complete debit including VAT and contribution
        """
        if expense_type.tva_on_margin:
            yield self._debit_ht(expense_type, ht + tva, **kwargs)
            yield self._credit_tva_on_margin(expense_type, tva, **kwargs)

        else:
            yield self._debit_ht(expense_type, ht, **kwargs)
        if tva != 0:
            yield self._debit_tva(expense_type, tva, **kwargs)

        if expense_type.contribution and self._has_contribution_module():
            yield from self.yield_contribution_entries(ht, **kwargs)

    def _yield_grouped_expenses(self, category: str = ""):
        """
        yield entries grouped by type
        """
        self.set_category(category)
        total = self.expense.get_total(category)
        if not total:
            return
        # An écriture summing all expenses
        yield self._credit(total, libelle=self.libelle, date=self.date)

        # An écriture for every category
        for charge in self.expense.get_lines_by_type(category):
            expense_type = charge[0].expense_type
            ht = sum([line.total_ht for line in charge])
            tva = sum([line.total_tva for line in charge])

            yield from self._write_complete_debit(
                expense_type, ht, tva, libelle=self.libelle, date=self.date
            )

    def _collect_more_expense_line_data(self, expense_line):
        """
        Collect expense line data that could be used when producing accounting
        operation lines

        Data returned here could be used in the associated Export Writer class
        """
        result = {
            "date": expense_line.date,
            "libelle": self.get_line_libelle(expense_line),
            "category": expense_line.category,
        }
        if getattr(expense_line, "supplier", None) is not None:
            result["supplier_label"] = expense_line.supplier.label
        return result

    def _yield_detailed_expenses(self, category: str = ""):
        """
        yield entries for each expense line
        """
        self.set_category(category)
        # An écriture per expense with all details in order
        for line in self.expense.get_lines(category):
            line_fixed_data = self._collect_more_expense_line_data(line)
            yield self._credit(
                line.total,
                **line_fixed_data,
            )

            expense_type = line.expense_type
            ht = line.total_ht
            tva = line.total_tva

            yield from self._write_complete_debit(
                expense_type,
                ht,
                tva,
                **line_fixed_data,
            )

    def yield_entries(self, category: str = ""):
        """
        Yield all the book entries for the current expensesheet
        """
        if self.expense.is_void:
            log.warn("Exporting a void expense : {0}".format(self.expense.id))
            return

        ungroup_expenses = bool(self.config.get("ungroup_expenses_ndf", "0") == "1")
        # Crédits
        if not ungroup_expenses:
            yield from self._yield_grouped_expenses(category)
        else:
            yield from self._yield_detailed_expenses(category)


@implementer(ITreasuryProducer)
class ExpenseExportProducer:
    """
    Export an expense to a Sage
    """

    _default_modules = (SageExpenseMain,)
    use_analytic = True
    use_general = True

    def __init__(self, context, request):
        self.request = request
        self.config = request.config
        self.modules = []
        for module in self._default_modules:
            self.modules.append(module(context, request))

    def _get_item_book_entries(self, expense, category=None):
        """
        Return book entries for a single expense
        """
        for module in self.modules:
            module.set_expense(expense)
            for entry in module.yield_entries(category):
                gen_line, analytic_line = entry
                if self.use_general:
                    yield filter_accounting_entry(gen_line)
                if self.use_analytic:
                    yield filter_accounting_entry(analytic_line)

    def get_item_book_entries(self, expenses, category=None):
        return list(self._get_item_book_entries(expenses, category))

    def get_book_entries(self, expenses, category=None):
        """
        Return the book entries for an expenselist
        """
        result = []
        for expense in expenses:
            result.extend(list(self._get_item_book_entries(expense, category)))
        return result

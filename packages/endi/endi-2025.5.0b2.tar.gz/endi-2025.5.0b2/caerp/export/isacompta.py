"""
 exports tools
"""
import logging
import csv
import datetime
from sqla_inspect.csv import CsvExporter
from caerp.utils.strings import format_amount


SAGE_COMPATIBLE_ENCODING = "iso-8859-15"


log = logging.getLogger(__name__)


class CsvWriter(CsvExporter):
    """
    Write  csv files
    :param datas: The datas to export list of dict
    :param headers: The translation tuple between input and output column
    names
    """

    encoding = SAGE_COMPATIBLE_ENCODING
    mimetype = "application/csv"
    extension = "txt"
    delimiter = ";"
    quotechar = '"'
    headers = ()
    amount_precision = 2
    quoting = csv.QUOTE_MINIMAL

    def __init__(self, context, request):
        super().__init__()
        if request:
            self.libelle_length = request.config.get_value(
                "accounting_label_maxlength",
                default=None,
                type_=int,
            )
        else:
            self.libelle_length = None

        if self.libelle_length is None:
            log.warning(
                "No accounting label length defined, fallback : " "truncating disabled"
            )
            self.libelle_length = 0

    def format_debit(self, debit):
        """
        Format the debit entry to get a clean float in our export
        12000 => 120,00
        """
        if debit == "":
            return 0
        else:
            return format_amount(debit, grouping=False, precision=self.amount_precision)

    def format_credit(self, credit):
        """
        format the credit entry to get a clean float
        """
        return self.format_debit(credit)

    def format_libelle(self, libelle):
        """
        truncate the libelle in order to suit the accounting software specs
        """
        if self.libelle_length > 0:
            return libelle[: self.libelle_length]
        else:
            return libelle

    def format_date(self, date_object):
        """
        format date for sage export
        """
        if isinstance(date_object, (datetime.date, datetime.datetime)):
            return date_object.strftime("%d%m%y")
        else:
            return date_object

    format_echeance = format_date


class InvoiceWriter(CsvWriter):
    """
    invoice csv writer
    """

    amount_precision = 5
    headers = (
        {"name": "num_caerp", "label": "Numéro de pièce"},
        {"name": "code_journal", "label": "Code Journal"},
        {"name": "date", "label": "Date de pièce"},
        {"name": "compte_cg", "label": "N° compte général"},
        {"name": "code_tva", "label": "Code tva"},
        {"name": "compte_tiers", "label": "Numéro de compte tiers"},
        {"name": "customer_name", "label": "Libellé pièce"},
        {"name": "libelle", "label": "Libellé mouvement"},
        {"name": "debit", "label": "Montant débit"},
        {"name": "credit", "label": "Montant crédit"},
        {"name": "num_analytique", "label": "Numéro analytique"},
    )


class PaymentWriter(CsvWriter):
    """
    Payment csv writer
    """

    amount_precision = 5
    headers = (
        {"name": "reference", "label": "Référence"},
        {"name": "code_journal", "label": "Code Journal"},
        {"name": "date", "label": "Date de pièce"},
        {"name": "compte_cg", "label": "N° compte général"},
        {"name": "code_tva", "label": "Code tva"},
        {"name": "compte_tiers", "label": "Numéro de compte tiers"},
        {"name": "customer_label", "label": "Libellé pièce"},
        {"name": "libelle", "label": "Libellé mouvement"},
        {"name": "debit", "label": "Montant débit"},
        {"name": "credit", "label": "Montant crédit"},
        {"name": "num_analytique", "label": "Numéro analytique"},
    )


class ExpenseWriter(CsvWriter):
    """
    Expense CsvWriter
    """

    headers = (
        {"name": "num_caerp", "label": "Numéro de pièce"},
        {"name": "code_journal", "label": "Code Journal"},
        {"name": "date", "label": "Date de pièce"},
        {"name": "compte_cg", "label": "N° compte général"},
        {"name": "code_tva", "label": "Code tva"},
        {"name": "compte_tiers", "label": "Numéro de compte tiers"},
        {"name": "user_name", "label": "Libellé pièce"},
        {"name": "libelle", "label": "Libellé mouvement"},
        {"name": "debit", "label": "Montant débit"},
        {"name": "credit", "label": "Montant crédit"},
        {"name": "num_analytique", "label": "Numéro analytique"},
    )


class SupplierInvoiceWriter(CsvWriter):
    headers = (
        {"name": "num_caerp", "label": "Numéro de pièce"},
        {"name": "code_journal", "label": "Code Journal"},
        {"name": "date", "label": "Date de pièce"},
        {"name": "compte_cg", "label": "N° compte général"},
        {"name": "code_tva", "label": "Code tva"},
        {"name": "compte_tiers", "label": "Numéro de compte tiers"},
        {"name": "supplier_label", "label": "Libellé pièce"},
        {"name": "libelle", "label": "Libellé mouvement"},
        {"name": "debit", "label": "Montant débit"},
        {"name": "credit", "label": "Montant crédit"},
        {"name": "num_analytique", "label": "Numéro analytique"},
    )

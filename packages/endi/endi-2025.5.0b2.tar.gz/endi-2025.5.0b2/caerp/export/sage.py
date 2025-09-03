"""
Sage exports tools
"""
import datetime
import logging

from sqla_inspect.csv import CsvExporter

from caerp.utils.strings import format_amount

SAGE_COMPATIBLE_ENCODING = "iso-8859-15"


log = logging.getLogger(__name__)


class SageCsvWriter(CsvExporter):
    """
    Write Sage csv files
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
        ret = libelle

        if self.libelle_length > 0:
            ret = libelle[: self.libelle_length]

        return ret.replace("\n", " ").replace("\r", " ")

    def format_date(self, date_object):
        """
        format date for sage export
        """
        if isinstance(date_object, (datetime.date, datetime.datetime)):
            return date_object.strftime("%d%m%y")
        else:
            return date_object

    format_echeance = format_date


class SageInvoiceCsvWriter(SageCsvWriter):
    """
    Sage invoice csv writer
    """

    amount_precision = 5
    headers = (
        {
            "name": "num_caerp",
            "label": "Numéro de pièce",
        },
        {"name": "code_journal", "label": "Code Journal"},
        {"name": "date", "label": "Date de pièce"},
        {"name": "compte_cg", "label": "N° compte général"},
        {"name": "num_caerp", "label": "Numéro de facture"},
        {"name": "compte_tiers", "label": "Numéro de compte tiers"},
        {"name": "code_tva", "label": "Code taxe"},
        {"name": "libelle", "label": "Libellé d'écriture"},
        {"name": "echeance", "label": "Date d'échéance"},
        {"name": "debit", "label": "Montant débit"},
        {"name": "credit", "label": "Montant crédit"},
        {"name": "type_", "label": "Type de ligne"},
        {"name": "num_analytique", "label": "Numéro analytique"},
    )


class SageExpenseCsvWriter(SageCsvWriter):
    """
    Expense CsvWriter
    """

    headers = (
        {"name": "num_caerp", "label": "Numéro de pièce"},
        {"name": "code_journal", "label": "Code Journal"},
        {"name": "date", "label": "Date de pièce"},
        {"name": "compte_cg", "label": "N° compte général"},
        {"name": "num_feuille", "label": "Numéro de note de dépenses"},
        {"name": "compte_tiers", "label": "Numéro de compte tiers"},
        {"name": "code_tva", "label": "Code taxe"},
        {"name": "libelle", "label": "Libellé d'écriture"},
        {"name": "debit", "label": "Montant débit"},
        {"name": "credit", "label": "Montant crédit"},
        {"name": "type_", "label": "Type de ligne"},
        {"name": "num_analytique", "label": "Numéro analytique"},
        {"name": "num_caerp", "label": "Référence"},
    )


class SagePaymentCsvWriter(SageCsvWriter):
    """
    Payment csv writer
    """

    amount_precision = 5
    headers = (
        {"name": "reference", "label": "Référence"},
        {"name": "code_journal", "label": "Code Journal"},
        {"name": "date", "label": "Date de pièce"},
        {"name": "compte_cg", "label": "N° compte général"},
        {"name": "mode", "label": "Mode de règlement"},
        {"name": "compte_tiers", "label": "Numéro de compte tiers"},
        {"name": "code_taxe", "label": "Code taxe"},
        {"name": "libelle", "label": "Libellé d'écriture"},
        {"name": "debit", "label": "Montant débit"},
        {"name": "credit", "label": "Montant crédit"},
        {"name": "type_", "label": "Type de ligne"},
        {"name": "num_analytique", "label": "Numéro analytique"},
    )


class SageExpensePaymentCsvWriter(SageCsvWriter):
    headers = (
        {"name": "reference", "label": "Référence"},
        {"name": "code_journal", "label": "Code Journal"},
        {"name": "date", "label": "Date de pièce"},
        {"name": "compte_cg", "label": "N° compte général"},
        {"name": "mode", "label": "Mode de règlement"},
        {"name": "compte_tiers", "label": "Numéro de compte tiers"},
        {"name": "code_taxe", "label": "Code taxe"},
        {"name": "libelle", "label": "Libellé d'écriture"},
        {"name": "debit", "label": "Montant débit"},
        {"name": "credit", "label": "Montant crédit"},
        {"name": "type_", "label": "Type de ligne"},
        {"name": "num_analytique", "label": "Numéro analytique"},
    )


class SageSupplierInvoiceCsvWriter(SageCsvWriter):
    headers = (
        {"name": "num_caerp", "label": "Numéro de pièce"},
        {"name": "code_journal", "label": "Code Journal"},
        {"name": "date", "label": "Date de pièce"},
        {"name": "compte_cg", "label": "N° compte général"},
        {"name": "remote_invoice_number", "label": "Numéro de facture"},
        {"name": "compte_tiers", "label": "Numéro de compte tiers"},
        {"name": "code_tva", "label": "Code taxe"},
        {"name": "libelle", "label": "Libellé d'écriture"},
        {"name": "debit", "label": "Montant débit"},
        {"name": "credit", "label": "Montant crédit"},
        {"name": "type_", "label": "Type de ligne"},
        {"name": "num_analytique", "label": "Numéro analytique"},
        {"name": "num_caerp", "label": "Référence"},
    )


class SageSupplierPaymentCsvWriter(SageCsvWriter):
    headers = (
        {"name": "num_caerp", "label": "Numéro de pièce"},
        {"name": "code_journal", "label": "Code Journal"},
        {"name": "date", "label": "Date de pièce"},
        {"name": "compte_cg", "label": "N° compte général"},
        {"name": "mode", "label": "Mode de règlement"},
        {"name": "compte_tiers", "label": "Numéro de compte tiers"},
        {"name": "code_taxe", "label": "Code taxe"},
        {"name": "libelle", "label": "Libellé d'écriture"},
        {"name": "debit", "label": "Montant débit"},
        {"name": "credit", "label": "Montant crédit"},
        {"name": "type_", "label": "Type de ligne"},
        {"name": "num_analytique", "label": "Numéro analytique"},
        {"name": "reference", "label": "Référence"},
    )

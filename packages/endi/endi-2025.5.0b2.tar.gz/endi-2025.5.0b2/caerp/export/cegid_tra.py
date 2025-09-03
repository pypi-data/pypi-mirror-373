import logging
from typing import Iterable
from io import StringIO
from zope.interface import implementer
from caerp.interfaces import ITreasuryWriter, ITreasuryInvoiceWriter

logger = logging.getLogger(__name__)

"""
IMPORT CEGID / QUADRA

Format : Texte, champs fixes

Écriture générale (Position / Longeur / Libellé) :
    1     1    Type = M
    2     8    Numéro de compte
    10    2    Code journal sur 2 caract. (blanc si renseigné en 111)
    12    3    N° folio (à initialiser à "000" si pas de folio)
    15    6    Date écriture (JJMMAA)
    21    1    Code libellé
    22    20   Libellé libre
    42    1    Sens Débit/Crédit (D/C)
    43    13   Montant en centimes signé (position 43=signe)
    56    8    Compte de contrepartie
    64    6    Date échéance (JJMMAA)
    70    2    Code lettrage
    72    3    Code statistiques
    75    5    N° de pièce sur 5 caractères maximum
    80    10   Code affaire
    90    10   Quantité
    100   8    Numéro de pièce jusqu'à 8 caractères
    108   3    Code devise (FRF ou EUR, Espace = FRF, ou Devise)
    111   3    Code journal sur 3 caract. (blanc si renseigné en 10 sur 2 caract.)
    114   1    Flag Code TVA géré dans l'écriture = O (oui)
    115   1    Code TVA = 0 à 9
    116   1    Méthode de calcul TVA = D (Débits) ou E (Encaissements)
    117   30   Libellé écriture sur 30 caract. (blanc si renseigné en 22 sur 20 caract.)
    147   2    Code TVA sur 2 caractères
    149   10   N° de pièce alphanumérique sur 10 caract.
    159   10   Réservé
    169   13   Montant dans la devise (en centimes signés position 169=signe)
    182   12   Pièce jointe à l'écriture

Écriture analytique (Position / Longeur / Libellé) :
    1     1    Type = I
    2     5    % de la répartition
    7     13   Montant répartition
    20    10   Code section
    30    10   Code nature

"""


@implementer(ITreasuryWriter)
class TraExporter:
    extension = "txt"
    mimetype = "text/plain"
    encoding = "iso-8859-1"
    headers = ""
    tra_datas = ""
    amount_precision = 5

    def __init__(self, context, request):
        pass

    def compute_amount_data(self, debit_amount, credit_amount):
        if debit_amount == None:
            amount_type = "C"
            amount = credit_amount
        else:
            amount_type = "D"
            amount = debit_amount

        # Force 2 digits precision
        if self.amount_precision > 2:
            amount = amount[: -(self.amount_precision - 2)]

        return amount_type, amount

    def format_general_entry(
        self,
        piece_number,
        code_journal,
        compte_cg,
        compte_tiers,
        date,
        echeance,
        libelle,
        amount_type,
        amount,
    ):
        # Type
        quadra_line = "M"

        # Numéro de compte sur 8 caractères
        if compte_tiers is not None and compte_tiers != "":
            quadra_line += compte_tiers.rjust(8)[:8]
        else:
            quadra_line += compte_cg.rjust(8)[:8]

        # Code journal de 2 caractères (à priori inutile)
        quadra_line += code_journal.ljust(2)[:2]

        # Folio
        quadra_line += "000"

        # Date
        quadra_line += date.ljust(6)[:6]

        # Filler d'un espace
        quadra_line += " "

        # Libellé de l'écriture
        quadra_line += libelle.ljust(20)[:20]

        # Sens
        quadra_line += amount_type

        # Signe du montant + ou - (apparement vide)
        quadra_line += " "

        # Montant sur 12 caractère remplis de zéros en retirant la virgule
        quadra_line += amount.replace(",", "").rjust(12, "0")[:12]

        # Contrepartie inutilisée pour l'instant
        quadra_line += "        "

        # Date d'échéance
        if echeance is None:
            quadra_line += "      "
        else:
            quadra_line += echeance.ljust(6)[:6]

        # Lettrage idem
        quadra_line += "     "

        # Numéro de pièce 5 caractere (on tronque)
        quadra_line += piece_number.ljust(5)[:5]

        # Filler de 20
        quadra_line += " ".rjust(20)

        # Numéro de pièce sur 8 caractère
        quadra_line += piece_number.ljust(8)[:8]

        # Devise
        quadra_line += "EUR"

        # Code journal
        quadra_line += code_journal.ljust(3)[:3]

        # Filler de 3
        quadra_line += "   "

        # Libellé de l'écriture sur 32
        quadra_line += libelle.ljust(32)[:32]

        # Numero de piece sur 10
        quadra_line += piece_number.ljust(10)[:10]

        # Filler de 73
        quadra_line += " ".ljust(73)

        return quadra_line

    def format_analytical_entry(self, amount, num_analytique):
        # Type
        quadra_line = "I"

        # Pourcentage de la répartition (100%)
        quadra_line += "10000"

        # Signe
        quadra_line += " "

        # Montant de la répartition
        quadra_line += amount.replace(",", "").rjust(12, "0")[:12]

        # Code analytique sur 10 caractère
        if num_analytique is None:
            logger.debug("Missing analytical account !")
            quadra_line += "          "
        else:
            quadra_line += num_analytique.ljust(10)

        # Code nature (inutilisé à priori) sur 10 caractère
        quadra_line += "          "

        return quadra_line

    def format_piece_number(self, row):
        if "num_caerp" in row:
            piece_number = row["num_caerp"]
        if "reference" in row:
            piece_number = row["reference"]
        return piece_number if piece_number else ""

    def format_row(self, row):
        """
        Format a row (dict of values) into a string in Cegid TRA format
        """
        logger.debug("format_row : {}".format(row))

        # Reading all fields from row
        piece_number = self.format_piece_number(row)
        journal_code = row["code_journal"]

        date = row["date"].strftime("%d%m%y")
        echeance = None
        if "echeance" in row:
            echeance = row["echeance"].strftime("%d%m%y")

        compte_number = row["compte_cg"]
        compte_tiers = None
        if "compte_tiers" in row:
            compte_tiers = row["compte_tiers"]
        libelle_ecriture = row["libelle"]

        debit_amount = None
        if "debit" in row:
            debit_amount = str(row["debit"])
        credit_amount = None
        if "credit" in row:
            credit_amount = str(row["credit"])
        amount_type, amount = self.compute_amount_data(debit_amount, credit_amount)

        analytic_number = None
        if "num_analytique" in row:
            analytic_number = row["num_analytique"]

        ## Creating entries
        general_entry = self.format_general_entry(
            piece_number,
            journal_code,
            compte_number,
            compte_tiers,
            date,
            echeance,
            libelle_ecriture,
            amount_type,
            amount,
        )
        analytical_entry = self.format_analytical_entry(amount, analytic_number)

        return general_entry + "\n" + analytical_entry + "\n"

    def set_datas(self, lines: Iterable):
        """
        Set the tabular datas that will be written in the output file

        :param lines: The lines produced by the associated ITreasuryProducer
        """
        logger.debug("set_datas : {}".format(len(lines)))

        for line in lines:
            # We only keep the analytical line as we will build
            # general and analytical entries from it
            # TODO : Should be done in the producer (use_general=False)
            if line["type_"] == "A":
                tra_line = self.format_row(line)
                self.tra_datas += tra_line

    def format_cell(self, column_name, value):
        """
        Format the given row, method needed for previzualisation

        Writer classes in the sqla_inspect package provides such methods
        """
        logger.debug("format_cell : {}, {}".format(column_name, value))

    def render(self) -> StringIO:
        """
        Produce the file data as a buffered file content like io.StringIO
        """
        tra_file = StringIO()
        tra_file.write(self.tra_datas)
        return tra_file


@implementer(ITreasuryInvoiceWriter)
class InvoiceWriter(TraExporter):
    headers = ""


class PaymentWriter(TraExporter):
    headers = ""

    # Specific for getting the payment piece_number
    def format_piece_number(self, row):
        return row["reference"]


class ExpenseWriter(TraExporter):
    headers = ""
    amount_precision = 2


class ExpensePaymentWriter(PaymentWriter):
    headers = ""
    amount_precision = 2


class SupplierInvoiceWriter(TraExporter):
    headers = ""
    amount_precision = 2


class SupplierPaymentWriter(TraExporter):
    headers = ""
    amount_precision = 2

from caerp.utils.compat import Iterable
import datetime
import logging
import decimal
from typing import (
    Optional,
    Set,
    Tuple,
    Union,
    List,
)

from caerp_base.models.base import DBSESSION
from caerp_base.models.utils import non_null_sum
from pyramid.request import Request

from caerp.compute.math_utils import floor_to_precision
from caerp.models.files import File
from caerp.models.task import (
    TaskLine,
    TaskLineGroup,
)
from caerp.models.task.invoice import Invoice
from caerp.models.task import Payment
from caerp.models.third_party import Customer
from caerp.utils.iteration import groupby

logger = logging.getLogger(__name__)

PAYMENT_EPSILON = 10000  # 10 centimes
REJECTED_MULTI_TVA = "a plusieurs TVA et est surpayée ou souspayée"
REJECTED_OVERPAY_MULTI_PAYMENT_YEAR = (
    "a des paiements sur plusieurs années et un excès de paiement"
)
REJECTED_PARTIAL_CANCEL = "est couverte par un avoir partiel"
REJECTED_NO_PRESTATION = (
    "ne contient aucune prestation de Service à la Personne (unité en heures)"
)


class RejectInvoice(Exception):
    """
    A rejected/ignored invoice with the reject reason as a text message.
    """

    def __init__(self, msg: str, invoice: Invoice):
        self.invoice = invoice
        self.msg = msg

    def __str__(self):
        return (
            f"<a href='/invoices/{self.invoice.id}'>{self.invoice.official_number}"
            f" ({self.invoice.internal_number})</a> {self.msg} :"
            " Ceci n'est pas supporté en mode SAP. Facture ignorée dans"
            " les attestations fiscales généres par caerp."
        )


def _taskline_to_sap_attestation_line(
    taskline: TaskLine,
    amount=None,
    quantity=None,
) -> "SAPTaskLine":
    """
    :param amount: overwrite the amount from the taskline
    """
    from caerp.plugins.sap.models.sap import SAPAttestationLine

    assert (
        taskline.date is not None
    ), "en mode SAP, on est pas censé avoir des taskline sans date"

    return SAPAttestationLine(
        customer=taskline.task.customer,
        company=taskline.task.company,
        category=taskline.product.name,
        product_id=taskline.product_id,
        date=taskline.date,
        unit=taskline.unity,
        quantity=quantity if quantity else taskline.quantity,
        amount=amount if amount else taskline.total(),
    )


class SAPAttestationLineService:
    """
    Handles mainly the transformation of Invoices into SAPAttestationLines

    Unsupported :
    - multi-TVA invoices (hard to implement reliably with partial payments)
    - Invoices cancelled by partial cancelinvoices

    Partly supported :
    - invoices having prestation lines over different years with partial
      payment (may lead to inconsistencies on attestation regeneration if only
      one of the attestations is regenerated)
    """

    def __init__(self):
        self._rejectlist = []

    def _record_reject(self, exception: RejectInvoice):
        self._rejectlist.append(exception)

    def _clear_rejects(self):
        self._rejectlist = []

    def get_rejects(self) -> List[RejectInvoice]:
        """
        Get the rejects after a query() call
        """
        return self._rejectlist

    def query(
        self,
        year: int,
        companies_ids: Set[int] = None,
        customers_ids: Set[int] = None,
    ) -> Iterable["SAPAttestationLine"]:
        if not year:
            raise ValueError("At least year should be mentioned")

        self._clear_rejects()
        invoices_query = self._get_invoices(year, companies_ids, customers_ids)
        sap_lines = self._invoices_to_sap_lines(
            invoices_query,
            year,
        )

        yield from sap_lines

    @staticmethod
    def sort_for_grouping(lines: List["SAPAttestationLine"]) -> None:
        """
        Sort (inplace) the list for further grouping within attestation
        """
        lines.sort(key=lambda x: (x.product_id, x.date.month, not x.is_service))

    @staticmethod
    def _get_invoices(
        year: int,
        companies_ids: Set[int],
        customers_ids: Set[int],
    ):
        query = Invoice.query()
        query = query.join(Invoice.line_groups)
        query = query.join(TaskLineGroup.lines)
        query = query.join(Invoice.customer)
        # exclude tasks without payments
        query = query.join(Invoice.payments)

        query = query.filter(
            Invoice.status == "valid",
            # We do not want cancelinvoices nor internalinvoice here
            Invoice.type_ == "invoice",
            # Exclude subcontracting : subcontracting entity handles
            # attesttation itself
            Customer.type == "individual",
            Payment.year == year,
        )
        if companies_ids:
            query = query.filter(Invoice.company_id.in_(companies_ids))
        if customers_ids:
            query = query.filter(Invoice.customer_id.in_(customers_ids))

        query = query.order_by(Invoice.company_id, Invoice.customer_id)
        return query.distinct()

    @staticmethod
    def _should_reject(
        invoice: Invoice,
        tvas: Set[int],
        payment_years: Set[int],
        prestations_lines_total: float,
    ) -> Tuple[bool, Optional[RejectInvoice]]:
        """
        Tells if the invoice should be rejected and why
        """
        msg = ""
        is_exactly_paid = abs(invoice.total_ttc() - invoice.paid()) <= PAYMENT_EPSILON
        is_over_paid = (invoice.paid() - invoice.total_ttc()) > PAYMENT_EPSILON

        if prestations_lines_total <= 0:
            msg = REJECTED_NO_PRESTATION
        elif len(list(tvas)) > 1 and not is_exactly_paid:
            msg = REJECTED_MULTI_TVA
        elif is_over_paid and len(payment_years) > 1:
            msg = REJECTED_OVERPAY_MULTI_PAYMENT_YEAR
        elif invoice.cancelinvoice_amount() > 0:
            msg = REJECTED_PARTIAL_CANCEL

        if msg:
            return True, RejectInvoice(msg, invoice)
        else:
            return False, None

    def _invoices_to_sap_lines(
        self,
        invoices: Iterable[Invoice],
        year: int,
    ) -> Iterable[Union["SAPAttestationLine", RejectInvoice]]:
        """
        This function is slow and should be used only for specific cases
        (partial payment).
        """
        for invoice in invoices:
            yield from self._invoice_to_sap_lines(invoice, year)

    def _invoice_to_sap_lines(
        self,
        invoice: Invoice,
        year: int,
    ) -> Iterable[Union["SAPAttestationLine", RejectInvoice]]:
        """
        Yield zero to several SAPAttestationLine

        Those can be :
        - service line : from a TaskLine considered as a service (where the
          unit is hours)
        - expense line : from a TaskLine considered as an expense (the others)
        - epsilon lines : when rounding operations give a leftover, we issue a
          copy of the latest service line with the leftover
        """
        tvas = set()

        prestations_lines = []
        expenses_lines = []
        prestations_lines_total = 0
        expenses_lines_total = 0

        for line in invoice.all_lines:
            tvas.add(line.tva)
            # negative tasklines will be counted either as prestation or as
            # expense depending on their unit
            # To have a discount accross prestation AND expense, use the propper
            # discount feature.
            if line.is_in_hours:
                prestations_lines_total += line.total()
                prestations_lines.append(line)
            else:
                expenses_lines_total += line.total()
                expenses_lines.append(line)
        lines_total = expenses_lines_total + prestations_lines_total
        payment_years = {p.date.year for p in invoice.payments}

        rejected, exception = self._should_reject(
            invoice,
            tvas,
            payment_years,
            prestations_lines_total,
        )
        if rejected:
            self._record_reject(exception)
            return

        paid = invoice.paid(year)
        total_ttc = invoice.total_ttc()

        paid_to_share = min(paid, total_ttc)
        if abs(paid_to_share - floor_to_precision(lines_total)) > 1000:
            # Fix #2565 : ratio is computed with the floor_to_precision
            # Also use decimal module to avoid imprecisions
            payment_ratio = decimal.Decimal(paid_to_share) / decimal.Decimal(
                floor_to_precision(lines_total)
            )
            payment_ratio = float(payment_ratio)
        else:
            payment_ratio = 1

        attestation_line = None
        covered_lines_sum = 0

        # How many expense € per prestation € ?
        expenses_ratio = float(
            decimal.Decimal(expenses_lines_total)
            / decimal.Decimal(prestations_lines_total)
        )

        for taskline in prestations_lines:
            line_total = taskline.total()

            # prestation part :
            # proratize the payments on different lines
            service_covered_amount = line_total * payment_ratio
            quantity = taskline.quantity * payment_ratio

            # expenses part :
            expenses_covered_amount = service_covered_amount * expenses_ratio

            # Ici on utilise round_floor=True pour être sûr de ne pas dépasser
            # le total (et que l'epsilon soit positif)
            service_covered_amount = floor_to_precision(
                service_covered_amount,
                round_floor=True,
            )
            expenses_covered_amount = floor_to_precision(
                expenses_covered_amount,
                round_floor=True,
            )
            # Somme utilisé pour identifier l'epsilon
            covered_lines_sum += service_covered_amount + expenses_covered_amount

            # We skip the lines not from the right year
            # But they still get their share
            if taskline.date.year == year or year in payment_years:
                attestation_line = _taskline_to_sap_attestation_line(
                    taskline,
                    service_covered_amount,
                    quantity,
                )
                yield attestation_line

                if expenses_lines_total > 0:
                    # Adopts the code_cg of the attestation_line
                    expense_line = attestation_line.duplicate(
                        amount=expenses_covered_amount,
                        quantity=1,  # discard the expenses quantity
                        unit="frais",
                    )
                    yield expense_line

        epsilon = paid_to_share - covered_lines_sum

        # The epsilon cent(s) will be given to the latest category
        if epsilon != 0 and attestation_line:
            epsilon_line = attestation_line.duplicate(quantity=0, amount=epsilon)
            yield epsilon_line


class SAPAttestationService:
    @classmethod
    def get_or_create(
        cls, attestation_cls, customer_id, year
    ) -> Tuple["SAPAttestation", bool]:
        instance = (
            attestation_cls.query()
            .filter_by(
                customer_id=customer_id,
                year=year,
            )
            .first()
        )

        if instance is not None:
            created = False
        else:
            created = True
            instance = attestation_cls(
                customer_id=customer_id,
                year=year,
            )
            DBSESSION().add(instance)
            DBSESSION().flush()
        return instance, created

    @classmethod
    def _generate_from_lines(
        cls,
        attestation_cls,
        customer,
        customer_lines: Iterable["SAPAttestationLine"],
        year: int,
        overwrite_existing: bool,
        request: Request,
    ) -> Tuple[Optional["cls"], bool]:
        """
        Generate or regenerate an attestation

        :return: the generated attestation (or None) and the indication wether
          there was an overwrite or not.
        """
        from caerp.plugins.sap.export.sap_attestation_pdf import (
            sap_attestation_pdf,
        )
        from caerp.plugins.sap.models.sap import SAPAttestationLine

        customer_lines = list(customer_lines)
        # Order by category (bricolage, jardinage), then date
        SAPAttestationLine.sort_for_grouping(customer_lines)
        summary = sum(customer_lines)
        attestation, created = cls.get_or_create(
            attestation_cls,
            customer_id=customer.id,
            year=year,
        )

        if not created and not overwrite_existing:
            return None, False
        else:
            # update amount on regenerate

            attestation.amount = summary.amount
            attestation.cesu_amount = cls.get_cesu_sum(attestation)
            if not created:
                # Don't know why the onupdate=datetime.now do not work here
                attestation.updated_at = datetime.datetime.now()
                attestation = DBSESSION().merge(attestation)

            data = sap_attestation_pdf(
                attestation,
                customer_lines,
                request,
            )

            # Overwrite existing file
            if attestation.files:
                file_obj = attestation.files[0]
            else:
                file_obj = File(parent_id=attestation.id)

            customer_name = f"{customer.lastname} {customer.firstname}"
            file_obj.name = "Attestation SAP {} {} {}.pdf".format(
                year, customer_name[:50], attestation.id
            )
            file_obj.description = "Attestation fiscale SAP {} pour {}".format(
                year, customer.name
            )
            file_obj.data = data  # calls File._set_data

            if created:
                DBSESSION().add(file_obj)
            else:
                DBSESSION().merge(file_obj)
            return attestation, not created

    @classmethod
    def get_cesu_sum(cls, attestation: "SAPAttestation") -> int:
        """
        Compute the sum of payments by CESU for that attestation
        """
        invoice_ids = (
            DBSESSION()
            .query(Invoice.id)
            .join(Invoice.line_groups)
            .join(TaskLineGroup.lines)
            .filter(
                Invoice.customer_id == attestation.customer_id,
                TaskLine.year == attestation.year,
            )
        )
        query = DBSESSION().query(non_null_sum(Payment.amount))
        query = query.filter(
            Payment.task_id.in_(invoice_ids),
            Payment.mode.ilike("%cesu%"),
        )
        return query.scalar()

    @classmethod
    def generate_bulk(
        cls,
        attestation_cls,
        companies_ids,
        customers_ids,
        regenerate_existing,
        year,
        request: Request,
    ) -> Tuple[List[Tuple["SAPAttestation", bool]], List[RejectInvoice]]:
        """
        Returns a list of the generated SAPAttestation and the list
        of rejected invoices.
        """
        line_service = SAPAttestationLineService()

        all_lines = line_service.query(
            year=year,
            companies_ids=companies_ids,
            customers_ids=customers_ids,
        )
        outlist = []
        for customer, customer_lines in groupby(all_lines, "customer"):
            attestation, overwritten = cls._generate_from_lines(
                attestation_cls,
                customer,
                customer_lines,
                year,
                overwrite_existing=regenerate_existing,
                request=request,
            )
            if attestation:
                outlist.append((attestation, overwritten))
        return outlist, line_service.get_rejects()

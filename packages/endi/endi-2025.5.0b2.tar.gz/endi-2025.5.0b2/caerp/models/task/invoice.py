"""
    Invoice model
"""
import datetime
import logging

from beaker.cache import cache_region
from caerp_base.models.base import DBSESSION, default_table_args
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, distinct
from sqlalchemy.orm import deferred, relationship
from zope.interface import implementer

from caerp.compute.math_utils import integer_to_amount
from caerp.compute.task.common import InvoiceCompute
from caerp.interfaces import IInvoice, IMoneyTask
from caerp.models.status import StatusLogEntry
from caerp.utils.datetimes import get_current_year

from .services import CancelInvoiceService, InvoiceService
from .task import Task

logger = logging.getLogger(__name__)


INVOICE_STATES = (
    ("waiting", "En attente"),
    ("paid", "Partiellement payée"),
    ("resulted", "Soldée"),
)


@implementer(IInvoice, IMoneyTask)
class Invoice(Task):
    """
    Invoice Model
    """

    __tablename__ = "invoice"
    __table_args__ = default_table_args
    __mapper_args__ = {
        "polymorphic_identity": "invoice",
    }
    invoice_computer = None

    id = Column(
        ForeignKey("task.id"),
        primary_key=True,
        info={
            "colanderalchemy": {"exclude": True},
        },
    )
    _caerp_service = InvoiceService

    # Template pour les noms des documents
    _number_tmpl = "{s.company.name} {s.date:%Y-%m} F{s.company_index}"
    _deposit_name_tmpl = "Facture d'acompte {0}"
    _sold_name_tmpl = "Facture de solde {0}"
    financial_year = Column(
        Integer,
        info={"colanderalchemy": {"title": "Année fiscale"}},
        default=get_current_year,
    )
    is_deposit = Column(
        Boolean(),
        default=False,
        info={"colanderalchemy": {"title": "Facture d'acompte ?"}},
    )
    exported = deferred(
        Column(
            Boolean(),
            info={"colanderalchemy": {"title": "A déjà été exportée ?"}},
            default=False,
        ),
        group="edit",
    )

    # Specific to Invoice
    # FIXME: Use PaidStatusHolderMixin ?
    paid_status = Column(
        String(10),
        default="waiting",
        info={
            "colanderalchemy": {
                "title": "Statut de la facture",
            }
        },
    )

    estimation_id = Column(ForeignKey("estimation.id"))

    # Le mode de facturation de l'affaire classic / progress
    PROGRESS_MODE = "progress"
    CLASSIC_MODE = "classic"
    invoicing_mode = deferred(Column(String(20), default="classic"), group="edit")

    # Relationships
    estimation = relationship(
        "Estimation",
        primaryjoin="Invoice.estimation_id==Estimation.id",
        back_populates="invoices",
        info={
            "colanderalchemy": {"exclude": True},
            "export": {"exclude": True},
        },
    )
    cancelinvoices = relationship(
        "CancelInvoice",
        back_populates="invoice",
        primaryjoin="CancelInvoice.invoice_id==Invoice.id",
        info={"colanderalchemy": {"exclude": True}},
    )
    valid_cancelinvoices = relationship(
        "CancelInvoice",
        primaryjoin="and_(CancelInvoice.invoice_id==Invoice.id, "
        "CancelInvoice.status=='valid')",
        info={"colanderalchemy": {"exclude": True}},
    )

    def _get_project_index(self, project):
        """
        Return the index of the current object in the associated project
        :param obj project: A Project instance in which we will look to get the
        current doc index
        :returns: The next number
        :rtype: int
        """
        return project.get_next_invoice_index()

    def _get_company_index(self, company):
        """
        Return the index of the current object in the associated company
        :param obj company: A Company instance in which we will look to get the
        current doc index
        :returns: The next number
        :rtype: int
        """
        return company.get_next_invoice_index()

    def set_deposit_label(self):
        self.name = self._deposit_name_tmpl.format(self.project_index)

    def set_sold_label(self):
        self.name = self._sold_name_tmpl.format(self.project_index)

    def set_project(self, project):
        self.project = project

    def gen_cancelinvoice(self, request, user):
        """
        Return a cancel invoice with self's informations
        """
        return self._caerp_service.gen_cancelinvoice(request, self, user)

    def get_next_row_index(self):
        return len(self.default_line_group.lines) + 1

    def is_resulted(self):
        """
        Check if the current paid amount covers the Invoice amount

        :rtype: bool
        """
        topay = self.topay()
        total = self.total()

        if total > 0 and topay <= 0:
            return True
        elif total < 0 and topay >= 0:
            return True
        elif total == 0:
            return True
        return False

    def compute_paid_status(self, request, force_resulted=False) -> str:
        """
        Compute the paid status of the current invoice
        """
        logger.debug("-> There still to pay : %s" % self.topay())

        if self.is_resulted() or force_resulted:
            status = "resulted"
        elif self.paid() != 0:
            status = "paid"
        else:
            status = "waiting"
        return status

    def historize_paid_status(self, user):
        """
        Records the current paid_status in history

        :param user: the user who just changed paid status.
        """
        status_record = StatusLogEntry(
            status=self.paid_status,
            user_id=user.id,
            comment="",
            state_manager_key="paid_status",
        )
        self.statuses.append(status_record)
        return self

    def __repr__(self):
        return "<{s.__class__.__name__} id:{s.id}> number:{s.official_number}".format(
            s=self
        )

    def __json__(self, request):
        datas = Task.__json__(self, request)
        datas.update(
            dict(
                financial_year=self.financial_year,
                exported=self.exported,
                estimation_id=self.estimation_id,
                topay_amount=integer_to_amount(self.topay(), precision=5),
                paid_status=self.paid_status,
            )
        )
        return datas

    def is_tolate(self):
        """
        Return True if a payment is expected since more than
        45 days
        """
        res = False
        if self.paid_status in ("waiting", "paid"):
            today = datetime.date.today()
            elapsed = today - self.date
            if elapsed > datetime.timedelta(days=45):
                res = True
            else:
                res = False
        return res

    @property
    def global_status(self):
        """
        hook on status and paid status to update css classes representing icons
        :return: a Sting
        """
        if self.paid_status == "paid":
            if self.date + datetime.timedelta(days=45) > datetime.date.today():
                return "partial_caution"
            else:
                return "partial_invalid"
        if self.paid_status == "waiting" and self.status == "valid":
            if self.date + datetime.timedelta(days=45) > datetime.date.today():
                return "caution"
            else:
                return "invalid"
        return self.status

    def _get_invoice_computer(self):
        """
        Return needed compute class depending on mode value
        :return: an instance of TaskCompute or TaskTtcCompute
        """
        if self.invoice_computer is None:
            self.invoice_computer = InvoiceCompute(self)
        return self.invoice_computer

    def cancelinvoice_amount(self):
        return self._get_invoice_computer().cancelinvoice_amount()

    def paid(self, year: int = None):
        """
        return the amount that has already been paid

        :param year: limit the considered payments to one year
        """
        return self._get_invoice_computer().paid(year)

    def topay(self):
        return self._get_invoice_computer().topay()

    def tva_paid_parts(self):
        return self._get_invoice_computer().tva_paid_parts()

    def tva_cancelinvoice_parts(self):
        return self._get_invoice_computer().tva_cancelinvoice_parts()

    def topay_by_tvas(self):
        return self._get_invoice_computer().topay_by_tvas()

    def compute_payments(self, payment_amount):
        return self._get_invoice_computer().compute_payments(payment_amount)


@implementer(IInvoice, IMoneyTask)
class CancelInvoice(Task):
    """
    CancelInvoice model
    Could also be called negative invoice
    """

    __tablename__ = "cancelinvoice"
    __table_args__ = default_table_args
    __mapper_args__ = {"polymorphic_identity": "cancelinvoice"}
    id = Column(
        Integer,
        ForeignKey("task.id"),
        primary_key=True,
        info={
            "colanderalchemy": {"exclude": True},
        },
    )
    # Common with Invoice
    financial_year = Column(
        Integer,
        info={"colanderalchemy": {"title": "Année fiscale"}},
        default=get_current_year,
    )
    exported = deferred(
        Column(
            Boolean(),
            info={"colanderalchemy": {"title": "A déjà été exportée ?"}},
            default=False,
        ),
        group="edit",
    )

    # Le mode de facturation de l'affaire classic / progress
    PROGRESS_MODE = "progress"
    CLASSIC_MODE = "classic"
    invoicing_mode = deferred(Column(String(20), default="classic"), group="edit")

    # Specific to CancelInvoice
    invoice_id = Column(
        Integer,
        ForeignKey("invoice.id"),
        info={
            "colanderalchemy": {
                "title": "Identifiant de la facture associée",
            }
        },
        default=None,
    )
    invoice = relationship(
        "Invoice",
        back_populates="cancelinvoices",
        primaryjoin="CancelInvoice.invoice_id==Invoice.id",
        info={"colanderalchemy": {"exclude": True}},
    )
    _caerp_service = CancelInvoiceService
    _number_tmpl = "{s.company.name} {s.date:%Y-%m} A{s.company_index}"

    def _get_project_index(self, project):
        """
        Return the index of the current object in the associated project
        :param obj project: A Project instance in which we will look to get the
        current doc index
        :returns: The next number
        :rtype: int
        """
        return project.get_next_cancelinvoice_index()

    def _get_company_index(self, company):
        """
        Return the index of the current object in the associated company
        :param obj company: A Company instance in which we will look to get the
        current doc index
        :returns: The next number
        :rtype: int
        """
        return company.get_next_cancelinvoice_index()

    def is_tolate(self):
        """
        Return False
        """
        return False

    def __repr__(self):
        return "<{s.__class__.__name__} id:{s.id}> number:{s.official_number}".format(
            s=self
        )

    def __json__(self, request):
        datas = Task.__json__(self, request)

        datas.update(
            dict(
                invoice_id=self.invoice_id,
                financial_year=self.financial_year,
                exported=self.exported,
            )
        )
        return datas

    @property
    def global_status(self):
        """
        hook on status and paid status to update css classes representing icons
        :return: a Sting
        """
        return self.status


# Usefull queries
def get_invoice_years(kw=None):
    """
        Return a cached query for the years we have invoices configured

    :param kw: is here only for API compatibility
    """

    @cache_region("long_term", "taskyears")
    def taskyears():
        """
        return the distinct financial years available in the database
        """
        query = DBSESSION().query(distinct(Invoice.financial_year))
        query = query.order_by(Invoice.financial_year)
        years = [year[0] for year in query]
        current = datetime.date.today().year
        if current not in years:
            years.append(current)
        return years

    return taskyears()

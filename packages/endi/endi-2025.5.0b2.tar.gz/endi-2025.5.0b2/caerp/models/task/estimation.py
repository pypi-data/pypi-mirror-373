"""
    The estimation model
"""

import datetime
import logging

from zope.interface import implementer
from beaker.cache import cache_region

from sqlalchemy import (
    Column,
    Integer,
    BigInteger,
    String,
    ForeignKey,
    Text,
    Boolean,
    Date,
    desc,
    distinct,
    func,
)
from sqlalchemy.orm import (
    relationship,
    deferred,
)
from sqlalchemy.ext.orderinglist import ordering_list
from caerp_base.models.base import (
    DBBASE,
    default_table_args,
    DBSESSION,
)
from caerp.compute.task.common import EstimationCompute
from caerp.compute.math_utils import integer_to_amount
from caerp.interfaces import (
    IMoneyTask,
)
from caerp.models.config import Config
from .services import (
    EstimationService,
)


from .task import Task

logger = logging.getLogger(__name__)


PAYMENTDISPLAYCHOICES = (
    (
        "NONE",
        "Les paiements ne sont pas affichés dans le PDF",
    ),
    (
        "SUMMARY",
        "Le résumé des paiements apparaît dans le PDF",
    ),
    (
        "ALL",
        "Le détail des paiements apparaît dans le PDF",
    ),
    (
        "ALL_NO_DATE",
        "Le détail des paiements, sans les dates, apparaît dans le PDF",
    ),
)

ESTIMATION_STATES = (
    ("waiting", "En attente"),
    ("sent", "Envoyé au client"),
    ("aborted", "Annulé"),
    ("signed", "Signé"),
)


@implementer(IMoneyTask)
class Estimation(Task):
    """
    Estimation Model
    """

    __tablename__ = "estimation"
    __table_args__ = default_table_args
    __mapper_args__ = {
        "polymorphic_identity": "estimation",
    }
    _caerp_service = EstimationService
    estimation_computer = None

    id = Column(
        ForeignKey("task.id"),
        primary_key=True,
        info={
            "colanderalchemy": {"exclude": True},
        },
    )
    signed_status = Column(
        String(10),
        default="waiting",
        info={
            "colanderalchemy": {
                "title": "Statut du devis",
            }
        },
    )
    geninv = Column(
        Boolean(),
        default=False,
        info={
            "colanderalchemy": {"title": "Factures générées ?"},
        },
    )
    # common with only invoices
    deposit = Column(
        Integer,
        info={
            "colanderalchemy": {"title": "Accompte (en %)"},
        },
        default=0,
    )
    manualDeliverables = deferred(
        Column(
            Integer,
            info={"colanderalchemy": {"title": "Configuration manuelle des paiements"}},
            default=0,
        ),
        group="edit",
    )
    paymentDisplay = deferred(
        Column(
            String(20),
            info={
                "colanderalchemy": {"title": "Affichage des paiements"},
            },
            default=PAYMENTDISPLAYCHOICES[0][0],
        ),
        group="edit",
    )
    validity_duration = Column(
        String(50),
        info={
            "colanderalchemy": {
                "title": "Limite de validité du devis",
            }
        },
    )

    payment_lines = relationship(
        "PaymentLine",
        order_by="PaymentLine.order",
        cascade="all, delete-orphan",
        back_populates="task",
        collection_class=ordering_list("order"),
        info={
            "colanderalchemy": {"title": "Échéances de paiement"},
        },
    )
    invoices = relationship(
        "Invoice",
        primaryjoin="Estimation.id==Invoice.estimation_id",
        order_by="Invoice.date",
        back_populates="estimation",
        info={
            "colanderalchemy": {"exclude": True},
        },
    )
    _number_tmpl = "{s.company.name} {s.date:%Y-%m} D{s.company_index}"

    def __repr__(self):
        return "<{s.__class__.__name__} id:{s.id} ({s.status})>".format(s=self)

    def __json__(self, request):
        if self.manualDeliverables == 1:
            payment_times = -1
        else:
            payment_times = len(self.payment_lines)

        result = Task.__json__(self, request)
        result.update(
            dict(
                deposit=self.deposit,
                deposit_amount_ttc=integer_to_amount(self.deposit_amount_ttc(), 5),
                manual_deliverables=self.manualDeliverables,
                manualDeliverables=self.manualDeliverables,
                paymentDisplay=self.paymentDisplay,
                validity_duration=self.validity_duration,
                payment_times=payment_times,
                payment_lines=[line.__json__(request) for line in self.payment_lines],
            )
        )
        return result

    def _get_project_index(self, project):
        """
        Return the index of the current object in the associated project
        :param obj project: A Project instance in which we will look to get the
        current doc index
        :returns: The next number
        :rtype: int
        """
        return project.get_next_estimation_index()

    def _get_company_index(self, company):
        """
        Return the index of the current object in the associated company
        :param obj company: A Company instance in which we will look to get the
        current doc index
        :returns: The next number
        :rtype: int
        """
        return company.get_next_estimation_index()

    def add_default_payment_line(self):
        self.payment_lines = [PaymentLine(description="Solde", amount=0)]
        return self

    @property
    def global_status(self):
        """
        hook on status and paid status to update css classes representing icons
        :return: a String
        """
        if self.signed_status == "aborted":
            return "closed"
        elif self.signed_status == "signed":
            return "neutral"
        elif self.signed_status == "sent":
            return "neutral"
        elif self.signed_status == "waiting":
            return "neutral"
        return self.status

    def _get_estimation_computer(self):
        """
        Return needed compute class depending on mode value
        :return: an instance of EstimationCompute or EstimationCompute ttc
        """
        if self.estimation_computer is None:
            self.estimation_computer = EstimationCompute(self)
        return self.estimation_computer

    def get_nb_payment_lines(self):
        return self._get_estimation_computer().get_nb_payment_lines()

    def paymentline_amounts_native(self):
        return self._get_estimation_computer().paymentline_amounts_native()

    def deposit_amounts_native(self):
        return self._get_estimation_computer().deposit_amounts_native()

    def deposit_amount_ht(self):
        return self._get_estimation_computer().deposit_amount_ht()

    def deposit_amount_ttc(self):
        return self._get_estimation_computer().deposit_amount_ttc()

    def paymentline_amount_ttc(self):
        return self._get_estimation_computer().paymentline_amount_ttc()

    def compute_ht_from_partial_ttc(self, partial_ttc: int) -> int:
        return self._get_estimation_computer().compute_ht_from_partial_ttc(partial_ttc)

    def sold(self):
        return self._get_estimation_computer().sold()

    def set_default_validity_duration(self):
        """
        Set last validity duration used by the company
        or CAE default config if none
        """
        default = Config.get_value("estimation_validity_duration_default")
        query = DBSESSION().query(Estimation.validity_duration)
        query = query.filter(Estimation.company_id == self.company_id)
        query = query.filter(Estimation.validity_duration != None)  # noqa
        query = query.order_by(desc(Estimation.id)).limit(1)
        last_duration = query.scalar()
        if last_duration:
            default = last_duration
        self.validity_duration = default

    def set_default_payment_display(self):
        self.paymentDisplay = Config.get_value(
            "estimation_payment_display_default", "NONE"
        )

    def update_payment_lines(self, request, payment_times=None):
        self._caerp_service.update_payment_lines(
            self, request, payment_times=payment_times
        )


class PaymentLine(DBBASE):
    """
    payments lines
    """

    __tablename__ = "estimation_payment"
    __table_args__ = default_table_args
    id = Column(
        Integer,
        primary_key=True,
        nullable=False,
    )
    task_id = Column(
        Integer,
        ForeignKey("estimation.id", ondelete="cascade"),
        info={
            "colanderalchemy": {
                "title": "Identifiant du document",
            }
        },
    )
    order = Column(Integer, info={"colanderalchemy": {"title": "Ordre"}}, default=1)
    description = Column(
        Text,
        info={"colanderalchemy": {"title": "Description"}},
    )
    amount = Column(
        BigInteger(),
        info={"colanderalchemy": {"title": "Montant"}},
    )
    date = Column(
        Date(), info={"colanderalchemy": {"title": "Date"}}, default=datetime.date.today
    )
    task = relationship(
        "Estimation",
        info={"colanderalchemy": {"exclude": True}},
        back_populates="payment_lines",
    )

    def duplicate(self):
        """
        duplicate a paymentline
        """
        return PaymentLine(
            order=self.order,
            amount=self.amount,
            description=self.description,
            date=datetime.date.today(),
        )

    def __repr__(self):
        return "<PaymentLine id:{s.id} task_id:{s.task_id} amount:{s.amount} date:{s.date}".format(
            s=self
        )

    def __json__(self, request):
        return dict(
            id=self.id,
            order=self.order,
            index=self.order,
            description=self.description,
            cost=integer_to_amount(self.amount, 5),
            amount=integer_to_amount(self.amount, 5),
            date=self.date.isoformat(),
            task_id=self.task_id,
        )

    def get_company_id(self):
        return self.task.company_id


# Usefull queries
def get_estimation_years(kw=None):
    """
        Return a cached query for the years we have estimations configured

    :param kw: is here only for API compatibility
    """

    @cache_region("long_term", "estimationyears")
    def estimationyears():
        query = DBSESSION().query(distinct(func.extract("YEAR", Estimation.date)))
        query = query.order_by(Estimation.date)
        years = [year[0] for year in query]
        current = datetime.date.today().year
        if current not in years:
            years.append(current)
        return years

    return estimationyears()

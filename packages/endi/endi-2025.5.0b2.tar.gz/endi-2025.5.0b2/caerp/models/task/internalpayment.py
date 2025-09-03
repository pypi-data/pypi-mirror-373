import logging

from sqlalchemy import (
    Column,
    ForeignKey,
)

from .payment import BaseTaskPayment
from .services import InternalPaymentService

logger = logging.getLogger(__name__)


class InternalPayment(BaseTaskPayment):
    __tablename__ = "internalpayment"
    __mapper_args__ = {
        "polymorphic_identity": "internalpayment",
    }
    internal = True
    _caerp_service = InternalPaymentService

    # Columns
    id = Column(
        ForeignKey("base_task_payment.id", ondelete="CASCADE"),
        primary_key=True,
        info={"colanderalchemy": {"exclude": True}},
    )

    @property
    def mode(self):
        return "Paiement interne"

    def sync_with_customer(self, request, action, **kw):
        return self._caerp_service.sync_with_customer(self, request, action, **kw)

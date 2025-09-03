import logging

from sqlalchemy import (
    Column,
    ForeignKey,
)

from .payment import BaseSupplierInvoicePayment

logger = logging.getLogger(__name__)


class InternalSupplierInvoiceSupplierPayment(BaseSupplierInvoicePayment):
    __tablename__ = "internalsupplier_payment"
    __mapper_args__ = {
        "polymorphic_identity": "internalsupplier_payment",
    }
    internal = True

    # Columns
    id = Column(
        ForeignKey("base_supplier_payment.id", ondelete="cascade"),
        primary_key=True,
        info={"colanderalchemy": {"exclude": True}},
    )

    @property
    def mode(self):
        return "Paiement interne"

from sqlalchemy import (
    Column,
    ForeignKey,
)
from sqlalchemy.orm import relationship

from .supplier_invoice import (
    SupplierInvoice,
    SupplierInvoiceLine,
)


class InternalSupplierInvoice(SupplierInvoice):
    __tablename__ = "internalsupplier_invoice"
    __mapper_args__ = {"polymorphic_identity": "internalsupplier_invoice"}
    internal = True

    id = Column(
        ForeignKey("supplier_invoice.id"),
        primary_key=True,
        info={"colanderalchemy": {"exclude": True}},
    )

    # relationship
    source_invoice = relationship(
        "InternalInvoice", uselist=False, back_populates="supplier_invoice"
    )
    source_cancelinvoice = relationship(
        "InternalCancelInvoice", uselist=False, back_populates="supplier_invoice"
    )

    @property
    def source(self):
        return self.source_invoice or self.source_cancelinvoice

    @classmethod
    def from_invoice(cls, invoice, supplier):
        """
        Create an instance based on the given invoice
        """
        instance = cls(
            remote_invoice_number=invoice.official_number,
            supplier=supplier,
            company=invoice.customer.source_company,
            date=invoice.date,
        )

        instance.lines.append(SupplierInvoiceLine.from_task(invoice))
        return instance

    def check_supplier_resulted(self, force_resulted: bool):
        # On force ce statut à être égal au statut de paiement
        # En effet, il n'y a pas répartition CAE/user sur les factures
        # fournisseurs internes donc on peut juste forcer
        self.supplier_paid_status = self.paid_status

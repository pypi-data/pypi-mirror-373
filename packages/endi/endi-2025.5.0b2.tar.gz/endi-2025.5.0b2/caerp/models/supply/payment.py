import datetime

from caerp_base.models.base import DBBASE, default_table_args
from caerp_base.models.mixins import TimeStampedMixin
from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.event import listen, remove
from sqlalchemy.orm import backref, declared_attr, relationship

from caerp.compute.math_utils import integer_to_amount
from caerp.models.export.accounting_export_log import (
    supplier_payment_accounting_export_log_entry_association_table,
)
from caerp.models.listeners import SQLAListeners


class BaseSupplierInvoicePayment(
    TimeStampedMixin,
    DBBASE,
):
    __tablename__ = "base_supplier_payment"
    __table_args__ = default_table_args
    __mapper_args__ = {
        "polymorphic_on": "type_",
        "polymorphic_identity": "base_supplier_payment",
    }
    internal = False
    precision = 2

    # Columns
    id = Column(Integer, primary_key=True)
    # Le type du paiement (permet de les différencier via le polymorphisme)
    type_ = Column(
        "type_",
        String(30),
        info={"colanderalchemy": {"exclude": True}},
        nullable=False,
    )
    supplier_invoice_id = Column(
        Integer,
        ForeignKey("supplier_invoice.id", ondelete="cascade"),
        info={
            "export": {"exclude": True},
        },
        nullable=True,
    )
    date = Column(
        DateTime(),
        default=datetime.datetime.now,
        info={"colanderalchemy": {"title": "Date de remise"}},
    )
    amount = Column(
        BigInteger(),
        info={"colanderalchemy": {"title": "Montant"}},
    )

    user_id = Column(
        ForeignKey("accounts.id", ondelete="set null"),
        info={"colanderalchemy": {"title": "Utilisateur ayant enregistré le paiement"}},
    )

    exported = Column(Boolean(), default=False)

    # relationships
    user = relationship(
        "User",
        info={"colanderalchemy": {"exclude": True}},
    )

    supplier_invoice = relationship(
        "SupplierInvoice",
        primaryjoin=(
            "SupplierInvoice.id==SupplierInvoiceSupplierPayment.supplier_invoice_id"
        ),
        back_populates="payments",
        info={
            "colanderalchemy": {"exclude": True},
            "export": {"exclude": True},
        },
    )

    exports = relationship(
        "SupplierPaymentAccountingExportLogEntry",
        secondary=supplier_payment_accounting_export_log_entry_association_table,
        back_populates="exported_supplier_payments",
    )

    @property
    def parent(self):
        return self.supplier_invoice

    def get_amount(self):
        return self.amount

    def __json__(self, request):
        return dict(
            id=self.id,
            mode="interne",
            amount=integer_to_amount(self.amount),
            date=self.date.isoformat(),
            bank_remittance_id=None,
        )

    def get_company_id(self):
        return self.supplier_invoice.company_id


class InterBankPaymentMixin:
    """
    Champs liés aux paiements voyageant d'un compte bancaise à un autre.

    (par oppoosition aux paiements internes)
    """

    @declared_attr
    def mode(cls):
        return Column(String(50))

    @declared_attr
    def bank_remittance_id(cls):
        return Column(
            String(255),
            info={"colanderalchemy": {"title": "Identifiant de remise en banque"}},
            nullable=True,
        )

    @declared_attr
    def bank_id(cls):
        return Column(
            Integer,
            ForeignKey("bank_account.id"),
            info={
                "export": {"exclude": True},
            },
            nullable=True,
        )


class SupplierInvoiceSupplierPayment(InterBankPaymentMixin, BaseSupplierInvoicePayment):
    """
    Payment issued from the CAE, to a Supplier

    The payment is linked to a SupplierInvoice, and covers the CAE percentage
    of it.
    """

    __tablename__ = "supplier_payment"
    __table_args__ = default_table_args
    __mapper_args__ = {"polymorphic_identity": "supplier_payment"}
    id = Column(
        ForeignKey("base_supplier_payment.id", ondelete="cascade"),
        primary_key=True,
        info={"colanderalchemy": {"exclude": True}},
    )
    bank = relationship(
        "BankAccount",
        backref=backref(
            "supplier_payments",
            order_by="SupplierInvoiceSupplierPayment.date",
            info={"colanderalchemy": {"exclude": True}},
        ),
    )

    sepa_waiting_payment = relationship(
        "SupplierInvoiceSupplierSepaWaitingPayment",
        primaryjoin="SupplierInvoiceSupplierPayment.id=="
        "foreign(SupplierInvoiceSupplierSepaWaitingPayment.payment_id)",
        back_populates="payment",
        uselist=False,
        single_parent=True,
        cascade="all, delete-orphan",
    )

    def appstruct(self):
        # Workaround : We rely on .__dict__ but this is not sufficient when
        # inheritance comes into play... (child fields are not returned by
        # __dict__) So we add'em by hand
        appstruct = super().appstruct()
        appstruct.update(
            dict(
                bank_remittance_id=self.bank_remittance_id,
                mode=self.mode,
                bank_id=self.bank_id,
            )
        )
        return appstruct

    def __json__(self, request):
        return dict(
            id=self.id,
            mode=self.mode,
            amount=integer_to_amount(self.amount),
            date=self.date.isoformat(),
            bank_remittance_id=self.bank_remittance_id,
        )


class SupplierInvoiceUserPayment(InterBankPaymentMixin, BaseSupplierInvoicePayment):
    """
    Payment issued from the CAE, to a user (contractor)

    The payment is linked to a SupplierInvoice, and covers the ES part of it.
    """

    __tablename__ = "supplier_invoice_user_payment"
    __table_args__ = default_table_args
    __mapper_args__ = {"polymorphic_identity": "supplier_invoice_user_payment"}
    id = Column(
        ForeignKey("base_supplier_payment.id", ondelete="cascade"),
        primary_key=True,
        info={"colanderalchemy": {"exclude": True}},
    )
    bank = relationship(
        "BankAccount",
        backref=backref(
            "user_payments",
            order_by="SupplierInvoiceUserPayment.date",
            info={"colanderalchemy": {"exclude": True}},
        ),
    )
    sepa_waiting_payment = relationship(
        "SupplierInvoiceUserSepaWaitingPayment",
        primaryjoin="SupplierInvoiceUserPayment.id=="
        "foreign(SupplierInvoiceUserSepaWaitingPayment.payment_id)",
        back_populates="payment",
        uselist=False,
        single_parent=True,
        cascade="all, delete-orphan",
    )

    waiver = Column(Boolean(), default=False)

    def appstruct(self):
        # Workaround : We rely on .__dict__ but this is not sufficient when
        # inheritance comes into play... (child fields are not returned by
        # __dict__) So we add'em by hand
        appstruct = super().appstruct()
        appstruct.update(
            dict(
                bank_remittance_id=self.bank_remittance_id,
                mode=self.mode,
                bank_id=self.bank_id,
                waiver=self.waiver,
            )
        )
        return appstruct

    def __json__(self, request):
        return dict(
            id=self.id,
            mode=self.mode,
            amount=integer_to_amount(self.amount),
            date=self.date.isoformat(),
            bank_remittance_id=self.bank_remittance_id,
        )


def update_if_waiver(mapper, conection, target):
    """
    If payment is a waiver payment mode is forced to waiving.
    """
    payment = target
    if payment.waiver:
        payment.mode = "par Abandon de créance"


def start_listening():
    listen(SupplierInvoiceUserPayment, "before_insert", update_if_waiver)
    listen(SupplierInvoiceUserPayment, "before_update", update_if_waiver)


def stop_listening():
    remove(SupplierInvoiceUserPayment, "before_insert", update_if_waiver)
    remove(SupplierInvoiceUserPayment, "before_update", update_if_waiver)


SQLAListeners.register(start_listening, stop_listening)

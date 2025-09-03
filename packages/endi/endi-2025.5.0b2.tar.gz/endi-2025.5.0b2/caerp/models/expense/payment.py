from sqlalchemy import (
    Column,
    Integer,
    Boolean,
    ForeignKey,
)
from caerp_base.models.base import (
    DBBASE,
    default_table_args,
)
from caerp.models.listeners import SQLAListeners
from caerp_base.models.mixins import (
    TimeStampedMixin,
)
from caerp.models.payments import PaymentModelMixin
from sqlalchemy.event import (
    listen,
    remove,
)
from sqlalchemy.orm import (
    relationship,
    backref,
)
from caerp.models.export.accounting_export_log import (
    expense_payment_accounting_export_log_entry_association_table,
)


class ExpensePayment(
    TimeStampedMixin,
    PaymentModelMixin,
    DBBASE,
):
    """
    Expense Payment entry
    """

    __tablename__ = "expense_payment"
    __table_args__ = default_table_args
    id = Column(Integer, primary_key=True)

    # est-ce un abandon de créance
    waiver = Column(Boolean(), default=False)
    expense_sheet_id = Column(
        Integer, ForeignKey("expense_sheet.id", ondelete="cascade")
    )
    user_id = Column(ForeignKey("accounts.id", ondelete="SET NULL"))
    user = relationship(
        "User",
        info={"colanderalchemy": {"title": "Auteur du paiement"}},
    )

    bank_id = Column(ForeignKey("bank_account.id"))
    bank = relationship(
        "BankAccount",
        backref=backref(
            "expense_payments",
            order_by="ExpensePayment.date",
            info={"colanderalchemy": {"exclude": True}},
        ),
    )
    expense = relationship(
        "ExpenseSheet",
        back_populates="payments",
    )
    exports = relationship(
        "ExpensePaymentAccountingExportLogEntry",
        secondary=expense_payment_accounting_export_log_entry_association_table,
        back_populates="exported_expense_payments",
    )
    sepa_waiting_payment = relationship(
        "ExpenseSepaWaitingPayment",
        primaryjoin="ExpensePayment.id==foreign(ExpenseSepaWaitingPayment.payment_id)",
        back_populates="payment",
        uselist=False,
        single_parent=True,
        cascade="all, delete-orphan",
    )

    @property
    def parent(self):
        return self.expense

    def __repr__(self):
        return (
            "<ExpensePayment id:{s.id} expense_sheet_id:{s.expense_sheet_id}"
            " amount:{s.amount} mode:{s.mode} date:{s.date}".format(s=self)
        )

    def get_company_id(self):
        return self.expense.company.id


def update_if_waiver(mapper, conection, target):
    """
    If payment is a waiver, payment mode is forced to waiving.
    """
    payment = target
    if payment.waiver:
        payment.mode = "par Abandon de créance"


def start_listening():
    listen(ExpensePayment, "before_insert", update_if_waiver)
    listen(ExpensePayment, "before_update", update_if_waiver)


def stop_listening():
    remove(ExpensePayment, "before_insert", update_if_waiver)
    remove(ExpensePayment, "before_update", update_if_waiver)


SQLAListeners.register(start_listening, stop_listening)

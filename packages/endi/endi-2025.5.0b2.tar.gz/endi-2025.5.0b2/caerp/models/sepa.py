"""
Crée un modèle pour les virements SEPA
"""
from caerp_base.models.base import DBBASE, default_table_args
from caerp_base.models.mixins import TimeStampedMixin
from sqlalchemy import Column, Date, ForeignKey, Integer, String
from sqlalchemy.orm import relationship


class BaseSepaWaitingPayment(TimeStampedMixin, DBBASE):
    """
    Model for SEPA waiting payments
    """

    __tablename__ = "base_sepa_waiting_payment"
    __table_args__ = default_table_args
    __mapper_args__ = {
        "polymorphic_identity": "base_sepa_waiting_payment",
        "polymorphic_on": "type_",
    }
    id = Column(Integer, primary_key=True)
    type_ = Column(String(120), nullable=False)
    amount = Column(Integer, nullable=False)
    node_id = Column(Integer, ForeignKey("node.id", ondelete="CASCADE"), nullable=False)
    # wait / paid / cancelled
    WAIT_STATUS = "wait"
    PAID_STATUS = "paid"
    # quand ce virement spécifique a échoué par exemple
    CANCELLED_STATUS = "cancelled"
    paid_status = Column(String(10), nullable=False, default=WAIT_STATUS)

    sepa_credit_transfer_id = Column(
        Integer,
        ForeignKey("sepa_credit_transfer.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Relationship
    sepa_credit_transfer = relationship(
        "SepaCreditTransfer",
        back_populates="sepa_waiting_payments",
    )


class ExpenseSepaWaitingPayment(BaseSepaWaitingPayment):
    """
    Model for SEPA waiting payments related to ExpenseSheet
    """

    __tablename__ = "expense_sepa_waiting_payment"
    __table_args__ = default_table_args
    __mapper_args__ = {
        "polymorphic_identity": "expense_sepa_waiting_payment",
    }
    id = Column(
        Integer,
        ForeignKey("base_sepa_waiting_payment.id", ondelete="CASCADE"),
        primary_key=True,
    )
    payment_id = Column(
        Integer, ForeignKey("expense_payment.id", ondelete="SET NULL"), nullable=True
    )
    expense_sheet = relationship(
        "ExpenseSheet",
        primaryjoin="ExpenseSheet.id==foreign(ExpenseSepaWaitingPayment.node_id)",
        back_populates="sepa_waiting_payments",
    )
    payment = relationship(
        "ExpensePayment",
        back_populates="sepa_waiting_payment",
    )


class SupplierInvoiceSupplierSepaWaitingPayment(BaseSepaWaitingPayment):
    """
    Model for Supplier SEPA waiting payments related to SupplierInvoice
    """

    __tablename__ = "supplier_invoice_supplier_sepa_waiting_payment"
    __table_args__ = default_table_args
    __mapper_args__ = {
        "polymorphic_identity": "supplier_invoice_supplier_sepa_waiting_payment",
    }
    id = Column(
        Integer,
        ForeignKey("base_sepa_waiting_payment.id", ondelete="CASCADE"),
        primary_key=True,
    )
    payment_id = Column(
        Integer, ForeignKey("supplier_payment.id", ondelete="SET NULL"), nullable=True
    )
    supplier_invoice = relationship(
        "SupplierInvoice",
        primaryjoin="SupplierInvoice.id==foreign("
        "SupplierInvoiceSupplierSepaWaitingPayment.node_id)",
        back_populates="supplier_sepa_waiting_payments",
    )
    payment = relationship(
        "SupplierInvoiceSupplierPayment", back_populates="sepa_waiting_payment"
    )


class SupplierInvoiceUserSepaWaitingPayment(BaseSepaWaitingPayment):
    """
    Model for User SEPA waiting payments related to SupplierInvoice
    """

    __tablename__ = "supplier_invoice_user_sepa_waiting_payment"
    __table_args__ = default_table_args
    __mapper_args__ = {
        "polymorphic_identity": "supplier_invoice_user_sepa_waiting_payment",
    }
    id = Column(
        Integer,
        ForeignKey("base_sepa_waiting_payment.id", ondelete="CASCADE"),
        primary_key=True,
    )
    payment_id = Column(
        Integer,
        ForeignKey("supplier_invoice_user_payment.id", ondelete="SET NULL"),
        nullable=True,
    )
    supplier_invoice = relationship(
        "SupplierInvoice",
        primaryjoin="SupplierInvoice.id==foreign(SupplierInvoiceUserSepaWaitingPayment.node_id)",
        back_populates="user_sepa_waiting_payments",
    )
    payment = relationship(
        "SupplierInvoiceUserPayment",
        primaryjoin="SupplierInvoiceUserPayment.id=="
        "foreign(SupplierInvoiceUserSepaWaitingPayment.payment_id)",
        back_populates="sepa_waiting_payment",
    )


class SepaCreditTransfer(TimeStampedMixin, DBBASE):
    """
    Model for SEPA transfers grouping ExpenseSheet and SupplierInvoice
    """

    __tablename__ = "sepa_credit_transfer"
    __table_args__ = default_table_args

    id = Column(Integer, primary_key=True)
    # Qui
    user_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    # Choix de l'utilisateur qui créé l'ordre de virement
    execution_date = Column(
        Date,
        nullable=False,
        info={
            "colanderalchemy": {
                "title": "Date d'exécution",
                "description": "Date à laquelle le virement sera exécuté, elle sera "
                "également utilisée pour dater les paiements.",
            }
        },
    )
    bank_account_id = Column(
        ForeignKey("bank_account.id", ondelete="SET NULL"),
        info={
            "colanderalchemy": {
                "title": "Compte bancaire",
                "description": "Compte bancaire depuis lequel le virement sera émis",
            }
        },
    )
    # Status
    OPEN_STATUS = "open"
    CLOSED_STATUS = "closed"
    CANCELLED_STATUS = "cancelled"
    status = Column(
        String(9),
        nullable=False,
        default=OPEN_STATUS,
        info={"colanderalchemy": {"title": "Statut"}},
    )
    # La référence du virement SEPA (mise quand le virement est envoyé)
    reference = Column(String(64), nullable=True, unique=True)
    # La version du XML SEPA
    sepa_pain_version = Column(
        String(12),
        default="001.001.09",
        info={
            "colanderalchemy": {
                "title": "Format du fichier d'ordre de virement",
                "description": "Version du standard 'pain' SEPA attendu par "
                "votre banque",
            }
        },
        nullable=False,
    )
    # Relation vers File pour le fichier SEPA XML
    file_id = Column(Integer, ForeignKey("file.id", ondelete="SET NULL"), nullable=True)
    file = relationship(
        "File",
        uselist=False,
        back_populates="sepa_credit_transfer_backref",
    )

    sepa_waiting_payments = relationship(
        "BaseSepaWaitingPayment",
        back_populates="sepa_credit_transfer",
    )
    bank_account = relationship("BankAccount")
    user = relationship("User")

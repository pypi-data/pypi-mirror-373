from typing import Optional

from caerp_base.models.base import DBBASE, default_table_args
from caerp_base.models.mixins import DuplicableMixin, OfficialNumberMixin
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship

from caerp.compute.math_utils import integer_to_amount
from caerp.compute.supplier_invoice import (
    SupplierInvoiceCompute,
    SupplierInvoiceLineCompute,
)
from caerp.models.export.accounting_export_log import (
    supplier_invoice_accounting_export_log_entry_association_table,
)
from caerp.models.node import Node
from caerp.models.project.mixins import BusinessLinkedModelMixin
from caerp.models.status import (
    PaidStatusHolderMixin,
    ValidationStatusHolderMixin,
    status_column,
)
from caerp.models.supply.mixins import LineModelMixin
from caerp.utils import strings

from ...utils.datetimes import format_date
from .services.supplier_invoice import (
    SupplierInvoiceLineService,
    SupplierInvoiceService,
)


class SupplierInvoice(
    DuplicableMixin,
    OfficialNumberMixin,
    SupplierInvoiceCompute,
    ValidationStatusHolderMixin,
    PaidStatusHolderMixin,
    Node,
):
    """
    A supplier invoice is linked :
    - 1..n SupplierOrder (constraint : same supplier and same percentage)
    - 1..n attachments (can map to multiple invoices form the supplier)
    - 0..n payments
    - 0..n lines (But that has little meaning with zero)
    """

    __tablename__ = "supplier_invoice"
    __table_args__ = default_table_args
    __mapper_args__ = {"polymorphic_identity": "supplier_invoice"}
    internal = False
    _caerp_service = SupplierInvoiceService
    validation_date_column = "date"

    __duplicable_fields__ = [
        "supplier_id",
        "cae_percentage",
        "company_id",
        "payer_id",
    ]

    # Attributes
    id = Column(
        ForeignKey("node.id"),
        primary_key=True,
        info={
            "colanderalchemy": {"exclude": True},
            "export": {"exclude": True},
        },
    )

    date = Column(
        DateTime(),
        info={"colanderalchemy": {"title": "Date de la facture"}},
    )

    supplier_id = Column(
        Integer,
        ForeignKey("supplier.id"),
        nullable=False,
        info={
            "export": {"exclude": True},
        },
    )

    cae_percentage = Column(
        Integer,
        default=100,
        info={
            "colanderalchemy": {"title": "pourcentage décaissé par la CAE"},
        },
    )
    exported = Column(
        Boolean(),
        info={
            "colanderalchemy": {
                "title": "A déjà été exportée vers le logiciel de comptabilité ?"
            },
            "export": {"label": "Exportée en compta ?"},
        },
        default=False,
    )

    remote_invoice_number = Column(
        String(255),
        info={
            "colanderalchemy": {
                "title": "Numéro de facture du fournisseur",
                "description": "Tel que mentionné sur le document fournisseur",
            },
            "export": {"label": "N° facture fournisseur"},
        },
        nullable=False,
        default="",
    )
    # Payments history is shared through paid_status_history
    # So they are not « full-featured statuses »
    worker_paid_status = status_column(default="waiting")
    supplier_paid_status = status_column(default="waiting")

    payer_id = Column(
        Integer,
        ForeignKey("accounts.id"),
        info={
            "export": {"exclude": True},
        },
    )

    # Relationships
    supplier = relationship(
        "Supplier",
        primaryjoin="Supplier.id==SupplierInvoice.supplier_id",
        back_populates="invoices",
        info={
            "colanderalchemy": {"exclude": True},
            "export": {"related_key": "label", "label": "Fournisseur"},
        },
    )

    payments = relationship(
        "BaseSupplierInvoicePayment",
        primaryjoin=(
            "SupplierInvoice.id==BaseSupplierInvoicePayment.supplier_invoice_id"
        ),
        back_populates="supplier_invoice",
        info={
            "colanderalchemy": {"exclude": True},
            "export": {"exclude": True},
        },
    )

    exports = relationship(
        "SupplierInvoiceAccountingExportLogEntry",
        secondary=supplier_invoice_accounting_export_log_entry_association_table,
        back_populates="exported_supplier_invoices",
        info={
            "colanderalchemy": {"exclude": True},
            "export": {"exclude": True},
        },
    )

    payer = relationship(
        "User",
        primaryjoin="SupplierInvoice.payer_id==User.id",
        info={
            "colanderalchemy": {"exclude": True},
            "export": {
                "formatter": lambda u: u.label,
                "label": "Entrepreneur (à rembourser)",
            },
        },
    )

    company = relationship(
        "Company",
        primaryjoin="Company.id==SupplierInvoice.company_id",
        info={
            "colanderalchemy": {"exclude": True},
            "export": {"related_key": "name", "label": "Enseigne"},
        },
    )

    lines = relationship(
        "SupplierInvoiceLine",
        cascade="all, delete-orphan",
        order_by="SupplierInvoiceLine.id",
        info={
            "colanderalchemy": {
                "title": "Entrées",
                "description": "Vous pouvez soit lister le détail de "
                + "votre facture soit vous contenter d'un total global.",
            },
            "export": {"exclude": True},
        },
        back_populates="supplier_invoice",
    )
    supplier_orders = relationship(
        "SupplierOrder",
        primaryjoin="SupplierInvoice.id==SupplierOrder.supplier_invoice_id",
        back_populates="supplier_invoice",
        info={
            "export": {"exclude": True},
        },
    )
    supplier_sepa_waiting_payments = relationship(
        "SupplierInvoiceSupplierSepaWaitingPayment",
        primaryjoin="SupplierInvoice.id==foreign(SupplierInvoiceSupplierSepaWaitingPayment.node_id)",
        back_populates="supplier_invoice",
        info={"colanderalchemy": {"exclude": True}},
        passive_deletes=True,
    )
    user_sepa_waiting_payments = relationship(
        "SupplierInvoiceUserSepaWaitingPayment",
        primaryjoin="SupplierInvoice.id==foreign(SupplierInvoiceUserSepaWaitingPayment.node_id)",
        back_populates="supplier_invoice",
        info={"colanderalchemy": {"exclude": True}},
        passive_deletes=True,
    )

    @property
    def cae_payments(self):
        from caerp.models.supply.payment import SupplierInvoiceSupplierPayment

        return [
            p for p in self.payments if isinstance(p, SupplierInvoiceSupplierPayment)
        ]

    @property
    def user_payments(self):
        from caerp.models.supply.payment import SupplierInvoiceUserPayment

        return [p for p in self.payments if isinstance(p, SupplierInvoiceUserPayment)]

    @property
    def global_status(self) -> str:
        """
        Combine .paid_status and .status
        """
        if self.paid_status == "paid":  # fully paid = resulted
            return "partial_caution"
        else:
            return self.status

    @property
    def supplier_label(self):
        if self.supplier is not None:
            return self.supplier.label
        else:
            return "indéfini"

    def check_worker_resulted(self, force_resulted: bool):
        self.worker_paid_status = self.get_resulted(
            force_resulted,
            self.worker_topay(),
            self.user_payments,
            self.worker_total,
        )

    def check_supplier_resulted(self, force_resulted: bool):
        self.supplier_paid_status = self.get_resulted(
            force_resulted,
            self.cae_topay(),
            self.cae_payments,
            self.cae_total,
        )

    def import_lines_from_order(self, supplier_order):
        """
        Copies all lines from a SupplierOrder
        """
        return self._caerp_service.import_lines(
            dest_line_factory=SupplierInvoiceLine,
            src_obj=supplier_order,
            dest_obj=self,
            source_id_attr="source_supplier_order_line_id",
        )

    def get_default_name(self):
        return "Facture {} du {}".format(self.supplier.company_name, self.date)

    @classmethod
    def filter_by_year(cls, query, year):
        return cls._caerp_service.filter_by_year(cls, query, year)

    def get_company_id(self):
        # for company detection in menu display
        return self.company_id

    def get_company(self):
        # for dashboard
        return self.company

    # FIXME: use StatusLogEntry (as invoice payment) for logging ?

    def duplicate(self, factory=None, **kwargs):
        ret = super().duplicate(factory, **kwargs)
        ret.lines = [l.duplicate() for l in self.lines]

        return ret

    def __repr__(self):
        return f"<{self.__class__.__name__} id:{self.id}> status:{self.status}"

    def __json__(self, request):
        return dict(
            id=self.id,
            date=self.date.date() if self.date else None,
            remote_invoice_number=self.remote_invoice_number,
            created_at=self.created_at.isoformat(),
            updated_at=self.updated_at.isoformat(),
            company_id=self.company_id,
            payer_id=self.payer_id,
            payer_name=self.payer.label if self.payer_id else "",
            paid_status=self.paid_status,
            # justified=self.justified,
            status=self.status,
            status_user_id=self.status_user_id,
            status_date=self.status_date,
            status_history=[
                status.__json__(request)
                for status in self.get_allowed_statuses(request)
            ],
            # From .supplier_orders
            orders_total=integer_to_amount(self.orders_total),
            orders_cae_total=integer_to_amount(self.orders_cae_total),
            orders_worker_total=integer_to_amount(self.orders_worker_total),
            orders_total_ht=integer_to_amount(self.orders_total_ht),
            orders_total_tva=integer_to_amount(self.orders_total_tva),
            internal=self.internal,
            cae_percentage=self.cae_percentage,
            supplier_name=self.supplier_label,
            supplier_id=self.supplier_id,
            lines=[line.__json__(request) for line in self.lines],
            payments=[payment.__json__(request) for payment in self.payments],
            cae_payments=[payment.__json__(request) for payment in self.cae_payments],
            user_payments=[payment.__json__(request) for payment in self.user_payments],
            attachments=[
                f.__json__(request) for f in self.children if f.type_ == "file"
            ],
            supplier_orders=[order.id for order in self.supplier_orders],
        )

    def has_waiting_payment(self) -> bool:
        return self.has_supplier_waiting_payment() or self.has_user_waiting_payment()

    def has_supplier_waiting_payment(self) -> bool:
        return self.get_supplier_waiting_payment() is not None

    def get_supplier_waiting_payment(self):
        for payment in self.supplier_sepa_waiting_payments:
            if payment.paid_status == payment.WAIT_STATUS:
                return payment

    def has_user_waiting_payment(self) -> bool:
        return self.get_user_waiting_payment() is not None

    def get_user_waiting_payment(self):
        for payment in self.user_sepa_waiting_payments:
            if payment.paid_status == payment.WAIT_STATUS:
                return payment


class SupplierInvoiceLine(
    LineModelMixin,
    BusinessLinkedModelMixin,
    DBBASE,
    SupplierInvoiceLineCompute,
):
    __tablename__ = "supplier_invoice_line"
    __table_args__ = default_table_args
    _caerp_service = SupplierInvoiceLineService
    parent_model = SupplierInvoice

    __duplicable_fields__ = LineModelMixin.__duplicable_fields__ + [
        "customer_id",
        "project_id",
        "business_id",
    ]

    id = Column(
        Integer,
        primary_key=True,
        info={"colanderalchemy": {"exclude": True}},
    )

    supplier_invoice_id = Column(
        Integer,
        ForeignKey("supplier_invoice.id", ondelete="cascade"),
        nullable=False,
        info={"colanderalchemy": {"exclude": True}},
    )

    supplier_invoice = relationship(
        "SupplierInvoice",
        primaryjoin="SupplierInvoice.id==SupplierInvoiceLine.supplier_invoice_id",
        info={
            "colanderalchemy": {"exclude": True},
            "export": {"exclude": True},
        },
        back_populates="lines",
    )
    source_supplier_order_line_id = Column(
        Integer,
        ForeignKey("supplier_order_line.id", ondelete="SET NULL"),
        nullable=True,  # NULL when created by hand
        info={"colanderalchemy": {"exclude": True}},
    )
    source_supplier_order_line = relationship(
        "SupplierOrderLine",
        info={
            "colanderalchemy": {"exclude": True},
            "export": {"exclude": True},
        },
    )

    expense_type = relationship(
        "ExpenseType",
        uselist=False,
        info={"colanderalchemy": {"exclude": True}},
    )

    def long_label(self):
        if self.expense_type is not None:
            tmpl = "{0.description} {amount}€ ({0.expense_type.label}) {date}"
        else:
            tmpl = "{0.description} {amount} {date}"
        return tmpl.format(
            self,
            amount=strings.format_amount(self.total, grouping=False),
            date=format_date(self.supplier_invoice.date),
        )

    @classmethod
    def linkable(cls, business):
        return cls._caerp_service.linkable(cls, business)

    @classmethod
    def query_linked_to(cls, target: "BusinessMetricsMixin"):
        return cls._caerp_service.query_linked_to(cls, target)

    @classmethod
    def total_expense(
        cls,
        query_filters=[],
        column_name="total_ht",
        tva_on_margin: Optional[bool] = None,
    ) -> int:
        return cls._caerp_service.total_expense(
            cls, query_filters, column_name, tva_on_margin
        )

    def __json__(self, request):
        ret = super(SupplierInvoiceLine, self).__json__(request)
        ret.update(
            dict(
                supplier_invoice_id=self.supplier_invoice_id,
            )
        )
        ret.update(
            dict(
                BusinessLinkedModelMixin.__json__(self, request),
            )
        )
        return ret

    def get_company_id(self):
        return self.supplier_invoice.company_id

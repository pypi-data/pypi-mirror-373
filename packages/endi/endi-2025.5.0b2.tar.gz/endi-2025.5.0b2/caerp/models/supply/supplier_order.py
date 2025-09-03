from sqlalchemy.orm import relationship
from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
)

from caerp_base.models.base import (
    DBBASE,
    default_table_args,
)
from caerp_base.models.mixins import DuplicableMixin
from caerp.models.node import Node
from caerp.models.status import ValidationStatusHolderMixin
from caerp.compute.supplier_order import (
    SupplierOrderCompute,
    SupplierOrderLineCompute,
)
from caerp.models.supply.mixins import LineModelMixin
from .services.supplier_order import SupplierOrderService


class SupplierOrder(
    DuplicableMixin,
    ValidationStatusHolderMixin,
    SupplierOrderCompute,
    Node,
):
    __tablename__ = "supplier_order"
    __table_args__ = default_table_args
    __mapper_args__ = {"polymorphic_identity": "supplier_order"}
    __duplicable_fields__ = [
        "company_id",
        "supplier_id",
        "cae_percentage",
    ]
    internal = False

    _caerp_service = SupplierOrderService

    id = Column(
        ForeignKey("node.id"),
        primary_key=True,
        info={"colanderalchemy": {"exclude": True}},
    )

    company_id = Column(
        Integer,
        ForeignKey("company.id"),
        info={
            "export": {"exclude": True},
            "colanderalchemy": {"exclude": True},
        },
        nullable=False,
    )

    supplier_id = Column(
        Integer,
        ForeignKey("supplier.id"),
        info={
            "export": {"exclude": True},
        },
    )

    supplier_invoice_id = Column(
        Integer,
        ForeignKey("supplier_invoice.id"),
        info={
            "export": {"exclude": True},
        },
        nullable=True,
    )

    cae_percentage = Column(
        Integer,
        default=100,
        info={
            "colanderalchemy": {"title": "pourcentage décaissé par la CAE"},
        },
    )

    # Relationships
    company = relationship(
        "Company",
        primaryjoin="Company.id==SupplierOrder.company_id",
        info={
            "colanderalchemy": {"exclude": True},
            "export": {"exclude": True},
        },
    )
    supplier = relationship(
        "Supplier",
        primaryjoin="Supplier.id==SupplierOrder.supplier_id",
        back_populates="orders",
        info={
            "colanderalchemy": {"exclude": True},
            "export": {"exclude": True},
        },
    )
    supplier_invoice = relationship(
        "SupplierInvoice",
        primaryjoin="SupplierInvoice.id==SupplierOrder.supplier_invoice_id",
        back_populates="supplier_orders",
        info={
            "export": {"exclude": True},
        },
    )

    lines = relationship(
        "SupplierOrderLine",
        cascade="all, delete-orphan",
        order_by="SupplierOrderLine.id",
        info={
            "colanderalchemy": {
                "title": "Entrées",
                "description": "Vous pouvez soit lister le détail de votre "
                + "commande soit vous contenter d'un total global.",
            }
        },
        back_populates="supplier_order",
    )

    @property
    def global_status(self):
        if self.supplier_invoice_id:
            return "invoiced"
        else:
            return self.status

    @classmethod
    def query_for_select(cls, valid_only=False, company_id=None, invoiced=None):
        return cls._caerp_service.query_for_select(
            cls,
            valid_only,
            company_id,
            invoiced,
        )

    @classmethod
    def filter_by_year(cls, query, year):
        return cls._caerp_service.filter_by_year(cls, query, year)

    # FIXME: factorize ?
    def check_validation_status_allowed(self, status, request, **kw):
        return self.validation_state_manager.check_allowed(
            status,
            self,
            request,
        )

    def get_company_id(self):
        # for company detection in menu display
        return self.company_id

    def get_company(self):
        # for dashboard
        return self.company

    def import_lines_from_order(self, supplier_order):
        """
        Copies all lines from a SupplierOrder
        """
        return self._caerp_service.import_lines(
            dest_line_factory=SupplierOrderLine,
            src_obj=supplier_order,
            dest_obj=self,
        )

    def __repr__(self):
        return f"<{self.__class__.__name__} id:{self.id}> status:{self.status}"

    def __json__(self, request):
        return dict(
            id=self.id,
            name=self.name,
            created_at=self.created_at.isoformat(),
            updated_at=self.updated_at.isoformat(),
            company_id=self.company_id,
            status=self.status,
            status_user_id=self.status_user_id,
            status_date=self.status_date.isoformat(),
            status_history=[
                status.__json__(request)
                for status in self.get_allowed_statuses(request)
            ],
            cae_percentage=self.cae_percentage,
            supplier_id=self.supplier_id,
            lines=[line.__json__(request) for line in self.lines],
            attachments=[
                f.__json__(request) for f in self.children if f.type_ == "file"
            ],
        )


class SupplierOrderLine(LineModelMixin, DBBASE, SupplierOrderLineCompute):
    __tablename__ = "supplier_order_line"
    __table_args__ = default_table_args

    id = Column(
        Integer,
        primary_key=True,
        info={"colanderalchemy": {"exclude": True}},
    )
    supplier_order_id = Column(
        Integer,
        ForeignKey("supplier_order.id", ondelete="cascade"),
        nullable=False,
        info={"colanderalchemy": {"exclude": True}},
    )

    supplier_order = relationship(
        "SupplierOrder",
        primaryjoin="SupplierOrder.id==SupplierOrderLine.supplier_order_id",
        info={
            "colanderalchemy": {"exclude": True},
            "export": {"exclude": True},
        },
        back_populates="lines",
    )

    def __json__(self, request):
        ret = super(SupplierOrderLine, self).__json__(request)
        ret.update(
            dict(
                supplier_order_id=self.supplier_order_id,
            )
        )
        return ret

    def get_company_id(self):
        return self.supplier_order.company_id

import datetime
from decimal import Decimal
from typing import (
    NamedTuple,
    Tuple,
    List,
    Optional,
)

from caerp_base.models.base import default_table_args
from sqlalchemy import (
    BigInteger,
    Column,
    ForeignKey,
    Integer,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from caerp.models.company import Company
from caerp.models.node import Node
from caerp.models.third_party import Customer
from caerp.utils.datetimes import get_current_year
from caerp.utils.strings import (
    format_quantity,
    is_hours,
)

from .services.attestation import (
    SAPAttestationLineService,
    SAPAttestationService,
    RejectInvoice,
)


class SAPAttestationLine(NamedTuple):
    """
    In-memory intermediary model for SAP attestations lines

    They can be agregated easily through regular python addition / sum()
    """

    company: Company
    customer: Customer
    category: str
    product_id: Optional[int]
    date: datetime.date
    quantity: float
    unit: str
    amount: Decimal  # TTC

    _caerp_service = SAPAttestationLineService

    def __add__(self, other):
        for attr in ("company", "customer"):
            if getattr(self, attr) != getattr(other, attr):
                raise ValueError(f"Cannot sum elements with different {attr} attrr")
        if self.unit != other.unit:
            if self.is_service and other.is_service:
                unit = "heures"
            else:
                unit = "unités diverses"
        else:
            unit = self.unit
        if self.product_id != other.product_id:
            product_id = None  # undefined
        else:
            product_id = self.product_id

        if other.amount < 0:  # other is a discount (negative taskline)
            # skip quantity : discount should never increase/decrease hours count
            # (but we sum amount)
            quantity = self.quantity
        else:
            quantity = self.quantity + other.quantity

        return SAPAttestationLine(
            company=self.company,
            customer=self.customer,
            # when grouping by product_id, keep first label :
            category=self.category,
            product_id=product_id,
            date=self.date,  # arbitrary but whynot
            unit=unit,
            quantity=quantity,
            amount=self.amount + other.amount,
        )

    def __radd__(self, other):
        # Allows to use sum()
        return self if other == 0 else self.__add__(other)

    def duplicate(self, **kwargs):
        """
        Duplicate, optionally with some different parameters provided as kwargs
        """
        params = self._asdict()
        params.update(kwargs)
        return SAPAttestationLine(**params)

    @property
    def month_label(self):
        return f"{self.date:%B %Y}".capitalize()

    @property
    def is_service(self):
        """
        Try to distinguish service (using hourly units) from other services
        """
        return is_hours(self.unit)

    @property
    def quantity_label(self):
        if self.is_service:
            marker = "s" if self.quantity > 1 else ""
            quantity = format_quantity(self.quantity)
            return f"{quantity} heure{marker}"
        else:
            return "autres frais"

    @classmethod
    def sort_for_grouping(cls, lines: List["SAPAttestationLine"]) -> None:
        return cls._caerp_service.sort_for_grouping(lines)


class SAPAttestation(Node):
    """
    Annual fiscal attestation for Service à la Personne

    Stores the attestation PDF within its Node.files attribute
    """

    __tablename__ = "sap_attestation"
    __table_args__ = (
        UniqueConstraint("year", "customer_id"),
        default_table_args,
    )
    __mapper_args__ = {"polymorphic_identity": "sap_attestation"}

    _caerp_service = SAPAttestationService

    id = Column(Integer, ForeignKey("node.id"), primary_key=True)
    customer_id = Column(
        Integer,
        ForeignKey("customer.id"),
    )
    amount = Column(
        BigInteger,
        info={
            "colanderalchemy": {
                "title": "Montant total réglé TTC",
            }
        },
        default=0,
    )
    cesu_amount = Column(
        BigInteger,
        info={
            "colanderalchemy": {
                "title": "Montant total réglé en CESU préfinancés",
            }
        },
        default=0,
    )
    year = Column(
        Integer,
        nullable=False,
        default=get_current_year,
        info={
            "colanderalchemy": {
                "title": "Année d'attestation",
            }
        },
    )
    # Relationships
    customer = relationship(
        "Customer",
        primaryjoin="Customer.id==SAPAttestation.customer_id",
    )

    @property
    def company(self):
        return self.customer.company

    def __str__(self):
        customer_name = self.customer.name
        company_name = self.company.name
        return f"Attestation SAP {self.year} {customer_name} ({company_name})"

    def get_cesu_sum(self):
        return self._caerp_service.get_cesu_sum(self)

    @classmethod
    def get_or_create(cls, *args, **kwargs) -> Tuple["SAPAttestation", bool]:
        return cls._caerp_service.get_or_create(cls, *args, **kwargs)

    @classmethod
    def generate_bulk(
        cls, *args, **kwargs
    ) -> Tuple[List[Tuple["SAPAttestation", bool]], List[RejectInvoice]]:
        return cls._caerp_service.generate_bulk(cls, *args, **kwargs)

    def get_company_id(self):
        return self.customer.company_id

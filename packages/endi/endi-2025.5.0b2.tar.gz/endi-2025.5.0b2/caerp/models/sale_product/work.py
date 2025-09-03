import logging
from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    String,
)
from sqlalchemy.orm import (
    relationship,
)
from caerp_base.models.base import (
    default_table_args,
)
from caerp.compute.math_utils import integer_to_amount
from .services import SaleProductWorkService
from .base import BaseSaleProduct


logger = logging.getLogger(__name__)


class SaleProductWork(BaseSaleProduct):
    """
    Work entity grouping several products
    """

    __tablename__ = "sale_product_work"
    __table_args__ = default_table_args
    __mapper_args__ = {"polymorphic_identity": __tablename__}
    __duplicable_fields__ = BaseSaleProduct.__duplicable_fields__ + [
        "title",
    ]
    id = Column(
        Integer,
        ForeignKey("base_sale_product.id", ondelete="cascade"),
        primary_key=True,
    )

    title = Column(String(255))

    items = relationship(
        "WorkItem",
        back_populates="sale_product_work",
        cascade="all, delete-orphan",
    )

    _caerp_service = SaleProductWorkService

    def __json__(self, request):
        result = BaseSaleProduct.__json__(self, request)
        result["title"] = self.title
        result["items"] = [{"id": item.id} for item in self.items]
        result["flat_cost"] = integer_to_amount(self.flat_cost(), 5)
        return result

    def sync_amounts(self, work_only=False):
        return self._caerp_service.sync_amounts(self, work_only)

    def duplicate(self, factory=None, **kwargs):
        return super().duplicate(
            factory,
            items=[item.duplicate() for item in self.items],
            **kwargs,
        )

    def flat_cost(self):
        """
        Renvoie le coût unitaire utilisé comme base pour les calculs
        """
        return self._caerp_service.flat_cost(self)

    def cost_price(self):
        return self._caerp_service.cost_price(self)

    def intermediate_price(self):
        return self._caerp_service.intermediate_price(self)

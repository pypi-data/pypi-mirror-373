"""
Models related to price study work management

PriceStudyWork
"""
from caerp_base.models.base import default_table_args
from sqlalchemy import (
    Column,
    String,
    ForeignKey,
    Boolean,
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.orderinglist import ordering_list

from .base import BasePriceStudyProduct
from .services import PriceStudyWorkService
from caerp.compute.math_utils import integer_to_amount


class PriceStudyWork(BasePriceStudyProduct):
    """
    price study entity grouping several price study work items

    Can be of two types

    Freely added
    Linked to an existing SaleProductWork

    """

    __tablename__ = "price_study_work"
    __table_args__ = default_table_args
    __mapper_args__ = {
        "polymorphic_on": "type_",
        "polymorphic_identity": __tablename__,
    }
    id = Column(
        ForeignKey("base_price_study_product.id", ondelete="CASCADE"), primary_key=True
    )
    title = Column(String(255))
    # Doit-on afficher le détail des prestations dans le document final ?
    display_details = Column(Boolean(), default=True)
    # Relationships
    items = relationship(
        "PriceStudyWorkItem",
        order_by="PriceStudyWorkItem.order",
        collection_class=ordering_list("order"),
        back_populates="price_study_work",
        cascade="all, delete",
    )

    _caerp_service = PriceStudyWorkService

    def __json__(self, request):
        result = BasePriceStudyProduct.__json__(self, request)
        result.update(
            dict(
                display_details=self.display_details,
                title=self.title,
                items=[{"id": item.id} for item in self.items],
                ttc=integer_to_amount(self.ttc(), 5),
                flat_cost=integer_to_amount(self.flat_cost(), 5),
            )
        )
        return result

    @classmethod
    def from_sale_product(cls, sale_product):
        instance = super(PriceStudyWork, cls).from_sale_product(sale_product)
        if sale_product.title:
            instance.title = sale_product.title

        from caerp.models.price_study.work_item import PriceStudyWorkItem

        for item in sale_product.items:
            PriceStudyWorkItem.from_work_item(instance, item)
        return instance

    def duplicate(self, from_parent=False, force_ht=False, remove_cost=False):
        """
        :param bool from_parent: We are duplicating the whole tree, the parent is not
        the same as the current's instance
        :param bool force_ht: We unable the computation based on supplier cost ?
        :param remove_cost: Should we set the costs to zero ?
        """
        instance = super().duplicate(from_parent, force_ht)
        instance.title = self.title
        instance.display_details = self.display_details
        for item in self.items:
            instance.items.append(
                item.duplicate(
                    from_parent=True, force_ht=force_ht, remove_cost=remove_cost
                )
            )
        return instance

    def sync_quantities(self):
        return self._caerp_service.sync_quantities(self)

"""
Models related to simple product management

SaleProductProduct

SaleProductMaterial

SaleProductWorkForce

SaleProductServiceDelivery

SaleProductStockOperation
"""
import logging
from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
)
from caerp_base.models.base import (
    default_table_args,
)
from .base import BaseSaleProduct


logger = logging.getLogger(__name__)


class SaleProductProduct(BaseSaleProduct):
    """ """

    __tablename__ = "sale_product_product"
    __table_args__ = default_table_args
    __mapper_args__ = {"polymorphic_identity": __tablename__}
    id = Column(
        Integer,
        ForeignKey("base_sale_product.id", ondelete="cascade"),
        primary_key=True,
    )


class SaleProductMaterial(BaseSaleProduct):
    """ """

    __tablename__ = "sale_product_material"
    __table_args__ = default_table_args
    __mapper_args__ = {"polymorphic_identity": __tablename__}
    id = Column(
        Integer,
        ForeignKey("base_sale_product.id", ondelete="cascade"),
        primary_key=True,
    )


class SaleProductWorkForce(BaseSaleProduct):
    """
    Main d'oeuvre
    """

    __tablename__ = "sale_product_work_force"
    __table_args__ = default_table_args
    __mapper_args__ = {"polymorphic_identity": __tablename__}
    id = Column(
        Integer,
        ForeignKey("base_sale_product.id", ondelete="cascade"),
        primary_key=True,
    )


class SaleProductServiceDelivery(BaseSaleProduct):
    """
    Prestation
    """

    __tablename__ = "sale_product_service_delivery"
    __table_args__ = default_table_args
    __mapper_args__ = {"polymorphic_identity": __tablename__}
    id = Column(
        Integer,
        ForeignKey("base_sale_product.id", ondelete="cascade"),
        primary_key=True,
    )

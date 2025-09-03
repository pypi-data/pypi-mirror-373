"""
    Models related to the treasury module
"""
from sqlalchemy import (
    Column,
    Integer,
    Text,
    ForeignKey,
    BigInteger,
)
from sqlalchemy.orm import (
    relationship,
    backref,
)

from caerp_base.models.base import (
    DBBASE,
    default_table_args,
)


class TurnoverProjection(DBBASE):
    """
    Turnover projection
    :param company_id: The company this projection is related to
    :param month: The month number this projection is made for
    :param year: The year this projection is made for
    """

    __tablename__ = "turnover_projection"
    __table_args__ = default_table_args
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("company.id", ondelete="cascade"))
    month = Column(Integer)
    year = Column(Integer)
    comment = Column(Text, default="")
    value = Column(BigInteger)
    company = relationship(
        "Company",
        backref=backref(
            "turnoverprojections",
            order_by="TurnoverProjection.month",
            cascade="all, delete-orphan",
            info={
                "colanderalchemy": {"exclude": True},
                "export": {"exclude": True},
            },
        ),
    )

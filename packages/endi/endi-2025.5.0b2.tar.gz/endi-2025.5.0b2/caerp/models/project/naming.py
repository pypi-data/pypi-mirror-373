from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import (
    relationship,
)

from caerp_base.models.base import (
    DBBASE,
    default_table_args,
)


class LabelOverride(DBBASE):
    """
    Allows to store information about label overriding

    E.g: « devis » becoming « bon de livraison » for « construction » business
    type.

    Each instance is a CAE-configuration about a name overriden for a
    business_type+task type combination.
    """

    __table_args__ = (
        UniqueConstraint("business_type_id", "label_key"),
        default_table_args,
    )
    __tablename__ = "label_override"

    SUPPORTED_LABEL_KEYS = ["estimation", "invoice", "cancelinvoice"]

    id = Column("id", Integer, primary_key=True)
    business_type_id = Column(
        ForeignKey("business_type.id", ondelete="CASCADE"),
        nullable=False,
    )
    label_key = Column(
        String(30),  # invoice/cancelinvoice/estimation/…
        info={
            "export": {"exclude": True},
        },
    )
    label_value = Column(
        String(100),
        nullable=False,
    )
    business_type = relationship(
        "BusinessType",
        info={"colanderalchemy": {"exclude": True}},
        back_populates="label_overrides",
    )

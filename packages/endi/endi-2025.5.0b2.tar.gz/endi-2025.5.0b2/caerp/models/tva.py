"""
    Model for tva amounts
"""

import deform.widget
from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Boolean,
    Text,
    not_,
)
from sqlalchemy.orm import (
    relationship,
)

from caerp.compute.math_utils import integer_to_amount
from caerp_base.models.base import (
    DBBASE,
    DBSESSION,
    default_table_args,
)


class Tva(DBBASE):
    __tablename__ = "tva"
    __table_args__ = default_table_args
    id = Column("id", Integer, primary_key=True)
    active = Column(Boolean(), default=True)
    name = Column("name", String(15), nullable=False)
    value = Column("value", Integer, nullable=False)
    compte_cg = Column("compte_cg", String(125), default="")
    code = Column("code", String(125), default="")
    compte_a_payer = Column(String(125), default="")
    mention = Column(Text)
    default = Column("default", Boolean())
    compte_client = Column("compte_client", String(125), default="")

    products = relationship(
        "Product",
        cascade="all, delete-orphan",
        back_populates="tva",
        order_by="Product.order",
    )

    @classmethod
    def query(cls, include_inactive=False):
        q = super(Tva, cls).query()
        if not include_inactive:
            q = q.filter(Tva.active == True)  # NOQA: E712
        return q.order_by("value")

    @classmethod
    def by_value(cls, value, or_none=False):
        """
        Returns the Tva matching this value
        """
        query = super(Tva, cls).query().filter(cls.value == value)
        if or_none:
            return query.one_or_none()
        else:
            return query.one()

    @classmethod
    def get_default(cls):
        return cls.query().filter_by(default=True).first()

    def __json__(self, request):
        return dict(
            id=self.id,
            value=integer_to_amount(self.value, 2),
            label=self.name,
            name=self.name,
            default=self.default,
            products=[product.__json__(request) for product in self.products],
        )

    @classmethod
    def unique_value(cls, value, tva_id=None):
        """
        Check that the given value has not already been attributed to a tva
        entry

        :param int value: The value currently configured
        :param int tva_id: The optionnal id of the current tva object (edition
        mode)
        :returns: True/False
        :rtype: bool
        """
        query = cls.query(include_inactive=True)
        if tva_id:
            query = query.filter(not_(cls.id == tva_id))

        return query.filter_by(value=value).count() == 0

    @classmethod
    def get_internal(cls):
        """
        Return the Tva used to configure Internal Invoices
        """
        query = cls.query().join(Product).filter(Product.internal == True)  # NOQA: E712
        return query.first()

    @classmethod
    def get_external(cls):
        return (
            cls.query()
            .join(Product)
            .filter(Product.internal == False)  # NOQA: E712
            .all()
        )

    @property
    def rate(self):
        """
        Return the display value

        20 for 20% tva rate
        """
        value = max(self.value, 0)
        return integer_to_amount(value, 2)

    @property
    def ratio(self):
        """
        Return the ratio applied

        0.2 for 20% tva rate
        """
        value = max(self.value, 0)
        return integer_to_amount(value, 4)


class Product(DBBASE):
    __tablename__ = "product"
    __table_args__ = default_table_args
    id = Column("id", Integer, primary_key=True)
    name = Column("name", String(125), nullable=False)
    order = Column(
        "order",
        Integer,
        nullable=False,
        default=0,
        info={"colanderalchemy": {"exclude": True}},
    )
    compte_cg = Column("compte_cg", String(125))
    active = Column(Boolean(), default=True)
    internal = Column(Boolean(), default=False)
    tva_id = Column(
        Integer,
        ForeignKey("tva.id", ondelete="cascade"),
        info={"colanderalchemy": {"exclude": True}},
    )
    tva = relationship(
        "Tva", back_populates="products", info={"colanderalchemy": {"exclude": True}}
    )
    # Belongs to urssaf_3p but by commodity we store it here
    urssaf_code_nature = Column(
        String(10),
        nullable=False,
        default="",
        info={"colanderalchemy": {"widget": deform.widget.HiddenWidget()}},
    )

    def __json__(self, request):
        return dict(
            id=self.id,
            name=self.name,
            label=self.name,
            compte_cg=self.compte_cg,
            tva_id=self.tva_id,
        )

    @classmethod
    def get_internal(cls):
        """
        Collect the products related to internal invoicing

        :rtype: SQLA query
        """
        query = (
            cls.query()
            .filter(cls.internal == True)  # NOQA E712
            .order_by(Product.order)
        )
        return query.all()

    @classmethod
    def get_external(cls):
        """
        Collect the products related to internal invoicing

        :rtype: SQLA query
        """
        query = cls.query().filter(cls.internal == False)  # NOQA E712
        return query.all()

    @classmethod
    def query(cls, include_inactive=False):
        q = super(Product, cls).query()
        if not include_inactive:
            q = q.join(cls.tva)
            q = q.filter(Product.active == True)  # NOQA E712
            q = q.filter(Tva.active == True)  # NOQA E712
        return q.order_by("order")

    @classmethod
    def first_by_tva_value(cls, tva_value, internal=False):
        try:
            tva = Tva.by_value(tva_value)
        except Exception:
            return None

        res = (
            DBSESSION()
            .query(Product.id)
            .filter(
                cls.active == True,  # NOQA E712
                cls.internal == internal,
            )
            .filter_by(tva_id=tva.id)
            .first()
        )
        if res is not None:
            res = res[0]
        return res

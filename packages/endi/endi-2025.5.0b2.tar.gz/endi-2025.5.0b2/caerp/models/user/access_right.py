import logging

from sqlalchemy import (
    Table,
    Column,
    Integer,
    String,
    ForeignKey,
)
from sqlalchemy.orm import (
    relationship,
)

from caerp_base.models.base import (
    DBBASE,
    default_table_args,
)
from caerp.consts.access_rights import ACCESS_RIGHTS
from caerp.forms import (
    EXCLUDED,
)

logger = logging.getLogger(__name__)


groups_access_rights = Table(
    "groups_access_rights",
    DBBASE.metadata,
    Column(
        "access_right_id", Integer, ForeignKey("access_rights.id", ondelete="CASCADE")
    ),
    Column("group_id", Integer, ForeignKey("groups.id", ondelete="CASCADE")),
    mysql_charset=default_table_args["mysql_charset"],
    mysql_engine=default_table_args["mysql_engine"],
)


class AccessRight(DBBASE):
    """
    Predefined Access Rights used in enDI
    """

    __tablename__ = "access_rights"
    __table_args__ = default_table_args

    id = Column(Integer, primary_key=True, info={"colanderalchemy": EXCLUDED})
    name = Column(
        String(255),
        nullable=False,
        info={"colanderalchemy": {"title": "Nom"}},
        unique=True,
    )

    groups = relationship(
        "Group", secondary=groups_access_rights, back_populates="access_rights"
    )

    @property
    def label(self):
        return ACCESS_RIGHTS.get(self.name, {}).get("label")

    @property
    def description(self):
        return ACCESS_RIGHTS.get(self.name, {}).get("description")

    @property
    def global_permissions(self):
        return ACCESS_RIGHTS.get(self.name, {}).get("global_permissions", [])

    @property
    def tags(self):
        return ACCESS_RIGHTS.get(self.name, {}).get("tags", [])

    @property
    def account_type(self):
        return ACCESS_RIGHTS.get(self.name, {}).get("account_type", "all")

    @property
    def categpry(self):
        return ACCESS_RIGHTS.get(self.name, {}).get("category", "Général")

    @property
    def rgpd(self):
        return ACCESS_RIGHTS.get(self.name, {}).get("rgpd", False)

    def __repr__(self):
        return f"<{self.__class__.name} id:{self.id} name:{self.name}>"

    def __json__(self, request):
        return dict(
            id=self.id,
            name=self.name,
            description=self.description,
            label=self.label,
            tags=self.tags,
            category=self.categpry,
            account_type=self.account_type,
            rgpd=self.rgpd,
        )

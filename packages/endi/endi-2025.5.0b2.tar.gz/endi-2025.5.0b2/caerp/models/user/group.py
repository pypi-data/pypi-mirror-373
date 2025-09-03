import logging

from sqlalchemy import (
    Table,
    Column,
    Integer,
    String,
    ForeignKey,
    Boolean,
)
from sqlalchemy.orm import (
    relationship,
    deferred,
)
from sqlalchemy.exc import NoResultFound

from caerp_base.models.base import (
    DBBASE,
    DBSESSION,
    default_table_args,
)
from caerp.forms import (
    EXCLUDED,
)
from caerp.consts.users import ACCOUNT_TYPES
from .access_right import groups_access_rights

logger = logging.getLogger(__name__)


USER_GROUPS = Table(
    "user_groups",
    DBBASE.metadata,
    Column("login_id", Integer, ForeignKey("login.id")),
    Column("group_id", Integer, ForeignKey("groups.id")),
    mysql_charset=default_table_args["mysql_charset"],
    mysql_engine=default_table_args["mysql_engine"],
)


class Group(DBBASE):
    """
    Available groups used in enDI
    """

    __tablename__ = "groups"
    __table_args__ = default_table_args
    id = Column(Integer, primary_key=True, info={"colanderalchemy": EXCLUDED})
    name = Column(
        String(30),
        nullable=False,
        info={
            "colanderalchemy": {
                "title": "Nom du rôle",
                "description": (
                    "Nom du rôle utilisé en interne par l’application. En minuscule, "
                    "sans accents et sans espaces."
                ),
            }
        },
    )
    label = Column(
        String(255),
        nullable=False,
        info={
            "colanderalchemy": {"title": "Libellé du rôle (utilisé dans l'interface)"}
        },
    )
    account_type = Column(
        String(14),
        default=ACCOUNT_TYPES["equipe_appui"],
        info={
            "colanderalchemy": {"title": "Type de compte pouvant disposer de ce rôle"}
        },
    )
    default_for_account_type = Column(
        Boolean(),
        default=False,
        info={
            "colanderalchemy": {
                "title": "Ce rôle est-il utilisé par défaut pour les nouveaux comptes ?"
            }
        },
    )
    editable = deferred(
        Column(
            Boolean(),
            default=True,
            info={"colanderalchemy": {"exclude": True}},
        )
    )
    users = relationship(
        "Login",
        secondary=USER_GROUPS,
        back_populates="_groups",
    )
    access_rights = relationship(
        "AccessRight",
        secondary=groups_access_rights,
        back_populates="groups",
    )

    def __repr__(self):
        return f"<Group {self.id}: {self.name} ({self.label})>"

    @classmethod
    def _find_one(cls, name_or_id):
        """
        Used as a creator for the initialization proxy
        """
        with DBSESSION.no_autoflush:
            res = DBSESSION.query(cls).get(name_or_id)
            if res is None:
                # We try with the id
                try:
                    res = DBSESSION.query(cls).filter(cls.name == name_or_id).one()
                except NoResultFound:
                    raise ValueError(f"Group {name_or_id} was not found")

        return res

    def __json__(self, request):
        return dict(name=self.name, label=self.label)

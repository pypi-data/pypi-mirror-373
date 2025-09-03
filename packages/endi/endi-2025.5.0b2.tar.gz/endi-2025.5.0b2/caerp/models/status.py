"""
Handle a consistent way the different statuses stored in DB

We handle several statuses (validation status, payment status, justification
status…).

This module handles two things :

- the SQLA fields to mix-in the implementors
- the optional historization of the statuses through StatusLogEntry
- and some status-related tools.

It does not handle state machine itself, see also ActionManager uses for state
machine stuff.
"""

import datetime
import logging

from sqlalchemy import (
    Column,
    DateTime,
    String,
    Integer,
    Text,
    ForeignKey,
    or_,
    Boolean,
)
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import (
    relationship,
)

from caerp_base.models.base import (
    DBBASE,
    default_table_args,
)
from caerp.consts.permissions import PERMISSIONS
from caerp.utils.strings import format_status_string

logger = logging.getLogger(__name__)


def status_date_column():
    """Generate a datetime column for status registration"""
    return Column(
        DateTime(),
        default=datetime.datetime.now,
        info={
            "colanderalchemy": {
                "title": "Date du dernier changement de statut (cache)",
            },
            "export": {"exclude": True},
        },
    )


def status_user_id_column():
    return Column(
        ForeignKey("accounts.id", ondelete="set null"),
        info={
            "colanderalchemy": {
                "title": "Dernier utilisateur à avoir modifié le document (cache)",
            },
            "export": {"exclude": True},
        },
    )


def status_user_relationship(user_id_column: str):
    """
    :param user_id_column: dotted form (`Model.column`) of column storing user
    id.
    """
    return relationship(
        "User",
        primaryjoin=f"{user_id_column}==User.id",
        info={
            "colanderalchemy": {"exclude": True},
            "export": {"exclude": True},
        },
    )


def status_comment_column():
    return Column(
        Text,
        info={
            "colanderalchemy": {"title": "Commentaires"},
            "export": {"exclude": True},
        },
        default="",
        nullable=False,
    )


def status_history_relationship(state_manager_key: str = None, **options):
    """
    :param state_manager_key: if ommited : relationship to all entries,
        including memos (they have no state_manager_key)
    :param options:
    :return:
    """
    primaryjoin = "Node.id == StatusLogEntry.node_id"
    if state_manager_key:
        primaryjoin = (
            f"and_({primaryjoin}, "
            f'StatusLogEntry.state_manager_key == "{state_manager_key}")'
        )
    if not options.get("viewonly") and not options.get("cascade"):
        options["cascade"] = "all, delete-orphan"

    return relationship(
        "StatusLogEntry",
        primaryjoin=primaryjoin,
        order_by="desc(StatusLogEntry.pinned), desc(StatusLogEntry.datetime), desc(StatusLogEntry.id)",
        back_populates="node",
        info={
            "colanderalchemy": {"exclude": True},
            "export": {"exclude": True},
        },
        **options,
    )


def status_column(default=""):
    return Column(
        String(10),
        default=default,
        info={"colanderalchemy": {"title": "Statut"}, "export": {"exclude": True}},
    )


class StatusLogEntry(DBBASE):
    __tablename__ = "status_log_entry"
    __table_args__ = default_table_args

    id = Column(Integer, primary_key=True)
    node_id = Column(ForeignKey("node.id", ondelete="cascade"))
    node = relationship(
        "Node",
        primaryjoin="StatusLogEntry.node_id==Node.id",
        back_populates="statuses",
    )
    # Valeur libre correspondant à une clé dans l'application
    # 'status', 'validation_status', 'paid_status', 'justification_status',
    # 'signed_status', ...
    state_manager_key = Column(String(40))

    label = Column(
        String(255),
        info={
            "colanderalchemy": {
                "title": "Titre",
            },
        },
        nullable=False,
        default="",
    )
    # ("public", "private", "management")
    visibility = Column(
        String(50),
        default="public",
        info={
            "colanderalchemy": {
                "title": "Visibilité",
            },
        },
        nullable=False,
    )
    status = status_column()
    comment = status_comment_column()
    datetime = status_date_column()
    user_id = status_user_id_column()
    pinned = Column(
        Boolean(),
        default=False,
        nullable=False,
        info={
            "colanderalchemy": {
                "title": "Mémo épinglé",
            },
        },
    )

    user = relationship(
        "User",
        primaryjoin="User.id==StatusLogEntry.user_id",
    )

    def __json__(self, request):
        from caerp.views.render_api import (
            status_css_class,
            status_icon,
        )

        result = {
            "id": self.id,
            "datetime": self.datetime,
            "status": "neutral pinned" if self.pinned else self.status,
            "label": self.label if self.label else format_status_string(self),
            "comment": self.comment,
            "visibility": self.visibility,
            "icon": status_icon(self),
            "css_class": status_css_class(self),
            "can_edit": request.has_permission(
                PERMISSIONS["context.edit_statuslogentry"], self
            ),
            "pinned": self.pinned,
        }
        if self.user is not None:
            result["user"] = self.user.label
        return result

    def get_company_id(self):
        from caerp.models.company import Company

        if isinstance(self.node, Company):
            return self.node_id
        if hasattr(self.node, "company_id"):
            return self.node.company_id
        elif hasattr(self.node, "get_company_id"):
            return self.node.get_company_id()
        return None


class ValidationStatusHolderMixin:
    """Holds a state machine for validation status and caches latest state

    state_manager_key : "validation_status"

    Would be clearer to name the model fields "validation_status",
    "validation_status_comment"… But for historical reason, and to avoid
    breaking stuff, they are named simply "status", "status_comment"…
    """

    @declared_attr
    def status(cls):
        return status_column(default="draft")

    @declared_attr
    def status_comment(cls):
        return status_comment_column()

    @declared_attr
    def status_user_id(cls):
        return status_user_id_column()

    @declared_attr
    def status_user(cls):
        return status_user_relationship(f"{cls.__name__}.status_user_id")

    @declared_attr
    def status_date(cls):
        return status_date_column()

    @declared_attr
    def validation_status_history(cls):
        return status_history_relationship("validation_status", viewonly=True)


class ValidationStatusHolderService:
    def __init__(self, *args, **kwargs):
        pass  # takes no parameter at the moment

    def waiting(self, *classes):
        """
        Documents waiting for validation

        :param *classes: the model classes to query (Node childs, implementing
          ValidationStatusHolderMixin)
        :returns: iterable query with documents.
        """
        from caerp.models.node import Node

        query = Node.query().with_polymorphic(classes)

        status_filters = [i.status == "wait" for i in classes]
        order_by = [c.status_date for c in classes]

        query = query.filter(or_(*status_filters))
        query = query.order_by(*order_by)
        return query


class PaidStatusHolderMixin:
    """
    Holds a state machine for paid status and caches latest state

    state_manager_key : "paid_status"

    Inheriting class must implement a `payment` property containing the list of
    payments.
    """

    @declared_attr
    def paid_status(cls):
        return status_column(default="waiting")

    @declared_attr
    def paid_status_comment(cls):
        return status_comment_column()

    @declared_attr
    def paid_status_user_id(cls):
        return status_user_id_column()

    @declared_attr
    def paid_status_date(cls):
        return status_date_column()

    @declared_attr
    def paid_status_history(cls):
        return status_history_relationship("paid_status", viewonly=True)

    @property
    def payments(self):
        """
        Must be implemented and (attr or property)

        Typical implementation : one-many relationship.
        :rtype list of PaymentModelMixin implementor:
        """
        raise NotImplementedError

    @property
    def total(self):
        """
        Must be implemented and provide a number
        """
        raise NotImplementedError

    def topay(self):
        """
        Must be implemented and provide a number
        """
        raise NotImplementedError

    def is_resulted(self, topay, total):
        """
        Return True/False if the document is resulted
        """
        if total > 0 and topay <= 0:
            return True
        elif total < 0 and topay >= 0:
            return True
        elif total == 0:
            return True
        return False

    def get_resulted(self, force_resulted, topay, payments, total):
        """
        Get the paid status resulting from the given elements

        Passing topay and total allows to handle split payments (eg : for
        supplier invoices)

        :param bool force_resulted: Has the paid status been forced to resulted
        ?
        :param int topay: The amount topay to consider
        :param list payments: The list of recorded payments
        :param int total: The total amount to consider
        """
        logger.debug("-> There still to pay : %s" % topay)

        if self.is_resulted(topay, total) or force_resulted:
            return "resulted"
        elif len(payments) > 0:
            return "paid"
        else:
            return "waiting"

    def compute_paid_status(self, request, force_resulted=False):
        """
        Check if the expense is resulted or not and set the appropriate status
        """
        return self.get_resulted(
            force_resulted,
            topay=self.topay(),
            payments=self.payments,
            total=self.total,
        )

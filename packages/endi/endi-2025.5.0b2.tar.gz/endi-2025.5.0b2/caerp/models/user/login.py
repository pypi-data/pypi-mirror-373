import logging
import datetime
from hashlib import md5
from sqlalchemy import (
    Column,
    Integer,
    Float,
    String,
    Boolean,
    DateTime,
    ForeignKey,
    not_,
)
from sqlalchemy.orm import (
    relationship,
    load_only,
)
from sqlalchemy.ext.associationproxy import association_proxy
from caerp_base.models.base import (
    DBBASE,
    default_table_args,
    DBSESSION,
)
from caerp.consts.users import ACCOUNT_TYPES
from caerp.models.user.user import User
from caerp.models.user.group import (
    USER_GROUPS,
    Group,
)

logger = logging.getLogger(__name__)


class Login(DBBASE):
    """
    Datas table containing login informations

    username/password
    """

    __tablename__ = "login"
    __table_args__ = default_table_args
    id = Column(Integer, primary_key=True, info={"colanderalchemy": {"exclude": True}})
    login = Column(
        String(64, collation="utf8mb4_bin"),
        unique=True,
        nullable=False,
        info={"colanderalchemy": {"title": "Identifiant"}},
    )

    pwd_hash = Column(
        String(100),
        info={
            "colanderalchemy": {
                "title": "Mot de passe",
            },
            "export": {"exclude": True},
        },
        nullable=False,
    )
    active = Column(
        Boolean(),
        info={"colanderalchemy": {"exclude": True}, "export": {"exclude": True}},
        default=True,
    )
    account_type = Column(
        String(14),
        nullable=False,
        default=ACCOUNT_TYPES["entrepreneur"],
        info={
            "colanderalchemy": {"title": "Type de compte"},
            "export": {"exclude": True},
        },
    )
    _groups = relationship(
        "Group",
        secondary=USER_GROUPS,
        info={"colanderalchemy": {"exclude": True}, "export": {"exclude": True}},
    )
    groups = association_proxy("_groups", "name", creator=Group._find_one)
    user_id = Column(Integer, ForeignKey("accounts.id"))
    user = relationship("User", info={"colanderalchemy": {"exclude": True}})
    supplier_order_limit_amount = Column(
        Float,
        nullable=True,
        info={
            "colanderalchemy": {
                "title": "Montant maximum HT autorisé pour l'autovalidation "
                "des commandes fournisseur",
                "description": "Dans le cas ou l'utilisateur est autorisé à "
                "valider ses propres commandes fournisseur. "
                "Pas de limite si non précisé.",
            }
        },
    )
    supplier_invoice_limit_amount = Column(
        Float,
        nullable=True,
        info={
            "colanderalchemy": {
                "title": "Montant maximum HT autorisé pour l'autovalidation "
                "des factures fournisseur",
                "description": "Dans le cas ou l'utilisateur est autorisé à "
                "valider ses propres factures fournisseur. "
                "Pas de limite si non précisé.",
            }
        },
    )
    estimation_limit_amount = Column(
        Float,
        nullable=True,
        info={
            "colanderalchemy": {
                "title": "Montant maximum HT autorisé pour l'autovalidation des "
                "devis",
                "description": "Dans le cas ou l'utilisateur est autorisé à "
                "valider ses propres devis. Pas de limite "
                "si non précisé.",
            }
        },
    )
    invoice_limit_amount = Column(
        Float,
        nullable=True,
        info={
            "colanderalchemy": {
                "title": "Montant maximum HT autorisé pour l'autovalidation des "
                "factures",
                "description": "Dans le cas ou l'utilisateur est autorisé à "
                "valider ses propres factures. Pas de limite "
                "si non précisé.",
            }
        },
    )

    def __init__(self, **kwargs):
        """
        Permet d'initialiser un Login avec des données

        Implémentation custom permettant de gérer le cas du "password"
        """
        if "password" in kwargs:
            self.set_password(kwargs.pop("password"))

        for key, value in kwargs.items():
            setattr(self, key, value)
        self.active = True

    @staticmethod
    def _encode_pass(password):
        """
        Return a md5 encoded password
        """
        password = password.encode("utf-8")
        return md5(password).hexdigest()

    def set_password(self, password):
        """
        Set the user's password
        """
        logger.info("Modifying password : '{0}'".format(self.login))
        self.pwd_hash = self._encode_pass(password)

    def auth(self, password):
        """
        Auth a user

        :param str password: The password to check
        :returns: True or False
        :rtype: bool
        """
        if password and self.active:
            if self.pwd_hash == self._encode_pass(password):
                return True
        return False

    @classmethod
    def query(cls, only_active=True):
        """
        Query users
        """
        query = super(Login, cls).query()
        if only_active:
            query = query.filter_by(active=True)

        return query

    @classmethod
    def unique_login(cls, login, login_id=None):
        """
        check that the given login is not yet in the database

            login

                A string for a login candidate

            login_id

                Optionnal login_id, if given, we will check all logins except
                this one (in case of edition)
        """
        query = cls.query(only_active=False)
        if login_id:
            query = query.filter(not_(cls.id == login_id))

        count = query.filter(cls.login == login).count()
        return count == 0

    @classmethod
    def unique_user_id(cls, user_id, login_id=None):
        """
        Check that no Login object is already associated to a User account with
        id user_id

            user_id

                A user id

            login_id

                Optionnal id, if given, we will check all logins except
                this one (in case of edition)
        """
        query = cls.query(only_active=False)
        if login_id:
            query = query.filter(not_(cls.id == login_id))

        return query.filter(cls.user_id == user_id).count() == 0

    @classmethod
    def id_from_login(cls, login):
        """
        Retrieve the Login instance matching with 'login'

        :param str login: The login string
        :returns: An id
        :rtype: int
        :raises: Error when no Login instance could be found
        """
        return cls.query().options(load_only("id")).filter_by(login=login).one().id

    @classmethod
    def find_by_login(cls, login, active=True):
        query = DBSESSION().query(cls)
        query = query.options(load_only("pwd_hash"))
        query = query.filter_by(login=login)
        if active:
            query = query.filter_by(active=True)
        return query.first()


class UserConnections(DBBASE):
    """
    Datas table containing user connections history by months
    """

    __tablename__ = "user_connections"
    __table_args__ = default_table_args
    user_id = Column(
        ForeignKey("accounts.id"), primary_key=True, info={"export": {"exclude": True}}
    )
    year = Column(
        Integer,
        primary_key=True,
        nullable=False,
        info={"colanderalchemy": {"title": "Année"}},
    )
    month = Column(
        Integer,
        primary_key=True,
        nullable=False,
        info={"colanderalchemy": {"title": "Mois"}},
    )
    month_last_connection = Column(
        DateTime,
        nullable=False,
        default=datetime.datetime.now,
        info={"colanderalchemy": {"title": "Dernière connexion"}},
    )
    user = relationship("User", info={"colanderalchemy": {"exclude": True}})

    def __init__(self, user=None, user_id=None, month_last_connection=None):
        if user is not None:
            self.user = user
            self.user_id = user.id
        elif user_id is not None:
            self.user_id = user_id
        else:
            raise ValueError("Either user or user_id must be provided")
        if month_last_connection is not None:
            self.year = month_last_connection.year
            self.month = month_last_connection.month
            self.month_last_connection = month_last_connection
        else:
            now = datetime.datetime.now()
            self.year = now.year
            self.month = now.month
            self.month_last_connection = now

    def __str__(self):
        return (
            f"<{self.__class__.__name__} {self.user_id} '{self.month_last_connection}'>"
        )

    def __repr__(self):
        return self.__str__()

    def __json__(self, request):
        user = User.query().filter_by(id=self.user_id).one()
        return dict(
            year=self.year,
            month=self.month,
            lastname=user.lastname,
            firstname=user.firstname,
            email=user.email,
            month_last_connection=self.month_last_connection,
        )

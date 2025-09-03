from sqlalchemy import (
    Table,
    Column,
    Integer,
    Boolean,
    String,
    ForeignKey,
)
from sqlalchemy.orm import (
    relationship,
    deferred,
    backref,
)
from sqlalchemy.event import listen
from caerp_base.models.base import (
    DBBASE,
    default_table_args,
    DBSESSION,
)
from caerp_base.models.types import JsonEncodedDict
from caerp_base.consts import CIVILITE_OPTIONS
from caerp.utils.strings import format_name
from caerp.models.tools import (
    set_attribute,
    get_excluded_colanderalchemy,
)
from caerp.models.listeners import SQLAListeners

COMPANY_EMPLOYEE = Table(
    "company_employee",
    DBBASE.metadata,
    Column("company_id", Integer, ForeignKey("company.id"), nullable=False),
    Column("account_id", Integer, ForeignKey("accounts.id"), nullable=False),
    mysql_charset=default_table_args["mysql_charset"],
    mysql_engine=default_table_args["mysql_engine"],
)


class User(DBBASE):
    """
    User model
    """

    __tablename__ = "accounts"
    __table_args__ = default_table_args
    id = Column(
        Integer,
        primary_key=True,
        info={"colanderalchemy": {"exclude": True}},
    )
    civilite = Column(
        String(10),
        info={
            "colanderalchemy": {
                "title": "Civilité",
            }
        },
        default=CIVILITE_OPTIONS[0][0],
        nullable=False,
    )

    lastname = Column(
        String(50),
        info={"colanderalchemy": {"title": "Nom"}},
        nullable=False,
    )

    firstname = Column(
        String(50),
        info={"colanderalchemy": {"title": "Prénom"}},
        nullable=False,
    )

    email = deferred(
        Column(
            String(100),
            info={
                "colanderalchemy": {
                    "title": "Adresse e-mail",
                }
            },
            nullable=False,
        ),
        group="edit",
    )

    compte_tiers = deferred(
        Column(
            String(30),
            info={
                "colanderalchemy": {
                    "title": "Compte tiers utilisé pour les notes de dépenses",
                    "section": "Notes de dépenses",
                }
            },
            default="",
        ),
        group="edit",
    )

    vehicle = deferred(
        Column(
            String(66),  # 50 + 1 + 15
            nullable=True,
            info={
                "colanderalchemy": {
                    "title": "Type de dépenses kilométriques",
                    "description": (
                        "Permet de restreindre les frais "
                        "kilométriques déclarables par l'entrepreneur"
                    ),
                    "section": "Notes de dépenses",
                }
            },
        )
    )

    vehicle_fiscal_power = Column(
        Integer,
        nullable=True,
        info={
            "colanderalchemy": {
                "title": "Puissance fiscale du véhicule",
                "description": (
                    "P.6 sur votre carte grise "
                    "nécessaire en cas de frais kilométriques"
                ),
                "section": "Notes de dépenses",
            }
        },
    )

    vehicle_registration = Column(
        String(15),
        nullable=True,
        info={
            "colanderalchemy": {
                "title": "Immatriculation du véhicule",
                "description": ("Nécessaire en cas de frais kilométriques"),
                "section": "Notes de dépenses",
            }
        },
    )

    photo_id = Column(
        ForeignKey("file.id"),
        info={"colanderalchemy": {"exclude": True}, "export": {"exclude": True}},
    )

    photo_is_publishable = Column(
        Boolean(),
        nullable=False,
        default=False,
        info={
            "colanderalchemy": {
                "title": "Photo publiable dans l'annuaire",
            }
        },
    )

    user_prefs = deferred(
        Column(
            JsonEncodedDict,
            info={"colanderalchemy": {"exclude": True}, "export": {"exclude": True}},
            default=None,
        ),
        group="edit",
    )

    """
    Marqueur "Comptes spéciaux"
    Non pris en compte pour la facturation enDI
    Edité directement en bdd
    """
    special = Column(
        Boolean(),
        nullable=False,
        default=False,
        info={"colanderalchemy": {"exclude": True}, "export": {"exclude": True}},
    )
    bank_account_bic = Column(
        String(12),
        info={
            "colanderalchemy": {
                "title": "BIC",
                "description": "BIC du compte bancaire",
                "section": "Compte bancaire",
            }
        },
    )
    bank_account_iban = Column(
        String(35),
        info={
            "colanderalchemy": {
                "title": "IBAN (utilisé pour les virements)",
                "description": "IBAN du compte bancaire, sans espace entre les chiffres",
                "section": "Compte bancaire",
            }
        },
    )
    bank_account_owner = Column(
        String(100),
        info={
            "colanderalchemy": {
                "title": "Titulaire",
                "description": "Civilité, Nom et Prénom du titulaire du "
                "compte (Nom et Prénom du compte par défaut)",
                "section": "Compte bancaire",
            }
        },
    )

    companies = relationship(
        "Company",
        secondary=COMPANY_EMPLOYEE,
        order_by="Company.name",
        info={
            "colanderalchemy": get_excluded_colanderalchemy("Enseignes"),
            "export": {"exclude": True},
        },
    )

    userdatas = relationship(
        "UserDatas",
        primaryjoin="User.id==UserDatas.user_id",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
        info={
            "colanderalchemy": {"exclude": True},
            "export": {"exclude": True},
        },
    )
    trainerdatas = relationship(
        "TrainerDatas",
        primaryjoin="User.id==TrainerDatas.user_id",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
        info={
            "colanderalchemy": {"exclude": True},
            "export": {"exclude": True},
        },
    )
    login = relationship(
        "Login",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
        info={
            "colanderalchemy": {"exclude": True},
            "export": {"exclude": True},
        },
    )
    connections = relationship(
        "UserConnections",
        back_populates="user",
        cascade="all, delete-orphan",
        order_by="UserConnections.month_last_connection.desc()",
        info={
            "colanderalchemy": {"exclude": True},
            "export": {"exclude": True},
        },
    )
    photo_file = relationship(
        "File",
        primaryjoin="File.id==User.photo_id",
        back_populates="user_photo_backref",
        info={"colanderalchemy": {"exclude": True}, "export": {"exclude": True}},
    )
    notifications = relationship(
        "Notification",
        primaryjoin="User.id==Notification.user_id",
        back_populates="user",
        cascade="all,delete,delete-orphan",
    )

    @classmethod
    def find_user(cls, value, *args, **kw):
        """
        Try to find a user instance based on the given value

        :param str value: The value that should match a user
        """
        result = cls.query().join(cls.login).filter_by(login=value).first()

        if result is None:
            value = value.split(" ")
            if len(value) >= 2:
                firstname = value[-1]
                lastname = " ".join(value[:-1])
                try:
                    query = cls.query()
                    query = query.filter_by(lastname=lastname)
                    query = query.filter_by(firstname=firstname)
                    result = query.one()
                except:
                    result = None
        return result

    def get_company(self, cid):
        """
        Retrieve the user's company with id cid

        :param int cid: The user's company id
        :returns: A Company instance
        :raises: `sqlalchemy.exc.NoResultFound` if no company can be found
        """
        from caerp.models.company import Company

        if not isinstance(cid, int):
            cid = int(cid)

        query = DBSESSION().query(Company)
        query = query.filter(Company.employees.any(User.id == self.id))
        query = query.filter(Company.id == cid)
        return query.one()

    def has_userdatas(self):
        """
        Return True if the current object has userdatas associated to it
        """
        from caerp.models.user.userdatas import UserDatas

        query = DBSESSION().query(UserDatas.id)
        query = query.filter(UserDatas.user_id == self.id)
        count = query.count()
        return count >= 1

    def __str__(self):
        return "<User {s.id} '{s.lastname} {s.firstname}'>".format(s=self)

    def __repr__(self):
        return self.__str__()

    def __json__(self, request):
        return dict(
            civilite=self.civilite,
            lastname=self.lastname,
            firstname=self.firstname,
        )

    @property
    def label(self):
        return format_name(self.firstname, self.lastname)

    @property
    def active_companies(self):
        """
        Return only enabled companies
        """
        return [company for company in self.companies if company.active]

    @property
    def active_company_ids(self):
        """
        Return only enabled companies ids
        """
        from caerp.models.company import Company

        query = DBSESSION().query(COMPANY_EMPLOYEE.c.company_id)
        query = query.filter(COMPANY_EMPLOYEE.c.account_id == self.id)
        query = query.join(Company).filter(Company.active == True)
        return [c[0] for c in query]

    @property
    def photo(self):
        return self.photo_file

    @photo.setter
    def photo(self, appstruct):
        if self.photo_file is not None and appstruct.get("delete"):
            DBSESSION().delete(self.photo_file)
        else:
            filename = appstruct.get("filename", "photo.png")
            if self.photo_file is None:
                from caerp.models.files import File

                self.photo_file = File()
            self.photo_file.name = filename
            self.photo_file.description = "Photo"
            self.photo_file.mimetype = appstruct.get("mimetype", "image/png")
            self.photo_file.size = appstruct.get("size", None)
            if appstruct.get("fp"):
                self.photo_file.data = appstruct["fp"]

    def get_company_id(self):
        return self.companies[0].id if self.companies else None


# Registering event handlers to keep datas synchronized
def sync_user_to_userdatas(source_key, userdatas_key):
    def handler(target, value, oldvalue, initiator):
        parentclass = initiator.parent_token.parent.class_
        if parentclass is User:
            if source_key == initiator.key:
                if target.userdatas is not None:
                    set_attribute(target.userdatas, userdatas_key, value, initiator)

    return handler


def start_listening():
    listen(
        User.firstname,
        "set",
        sync_user_to_userdatas("firstname", "coordonnees_firstname"),
    )
    listen(
        User.lastname, "set", sync_user_to_userdatas("lastname", "coordonnees_lastname")
    )
    listen(User.email, "set", sync_user_to_userdatas("email", "coordonnees_email1"))


SQLAListeners.register(start_listening)

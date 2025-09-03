from typing import Optional

from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    Date,
    String,
)
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declared_attr

from caerp_base.models.base import (
    DBBASE,
    default_table_args,
)
from caerp.models.node import Node
from caerp.consts.insee_departments import DEPARTMENTS
from caerp.consts.insee_countries import COUNTRIES
from caerp.models.third_party import Customer
from caerp.models.status import (
    status_column,
    status_comment_column,
    status_history_relationship,
    status_user_id_column,
    status_user_relationship,
    status_date_column,
)


class UrssafCustomerRegistrationStatus(Node):
    __tablename__ = "urssaf_customer_registration_status"
    __table_args__ = default_table_args
    __mapper_args__ = {
        "polymorphic_identity": __tablename__,
    }

    id = Column(ForeignKey("node.id"), primary_key=True)
    data_id = Column(ForeignKey("urssaf_customer_data.id", ondelete="cascade"))
    data = relationship(
        "UrssafCustomerData",
        back_populates="registration_status",
    )

    @declared_attr
    def status(cls):
        """
        Statuts:

        disabled (désactivé)
        wait (en attented de validation)
        valid (validé par le client)
        """
        return status_column(default="wait")

    @declared_attr
    def comment(cls):
        return status_comment_column()

    @declared_attr
    def user_id(cls):
        return status_user_id_column()

    @declared_attr
    def user(cls):
        return status_user_relationship(f"{cls.__name__}.user_id")

    @declared_attr
    def status_date(cls):
        return status_date_column()

    @declared_attr
    def urssaf3p_registration_status_history(cls):
        return status_history_relationship(
            "urssaf3p_registration_status", viewonly=True
        )


class UrssafCustomerData(DBBASE):
    """Champs demandés pour l'avance immédiate"""

    __tablename__ = "urssaf_customer_data"

    id = Column(Integer, primary_key=True)
    client_id = Column(
        String(80),  # On prend de la marge
        info={"colanderalchemy": {"exclude": True, "title": "Identifiant Urssaf"}},
        nullable=True,
    )
    customer_id = Column(
        ForeignKey(Customer.id, ondelete="CASCADE"),
        nullable=False,
        info={"colanderalchemy": {"exclude": True}},
    )
    customer = relationship(
        Customer,
        backref=backref(
            "urssaf_data",
            uselist=False,
            cascade="all, delete-orphan",
            info={"colanderalchemy": {"exclude": True}},
        ),
        info={"colanderalchemy": {"exclude": True}},
    )
    # Champ stockant les données (code, libellé de voie ...) complétant les données
    # déjà existantes au niveau du client
    street_type = Column(
        String(4),
        nullable=True,
        info={"colanderalchemy": {"title": "Type de voie"}},
        default="",
    )
    street_name = Column(
        String(28),
        info={"colanderalchemy": {"title": "Libellé de la voie"}},
    )
    street_number = Column(
        String(12), info={"colanderalchemy": {"title": "Numéro de la voie"}}, default=""
    )
    street_number_complement = Column(
        String(5),
        info={"colanderalchemy": {"title": "Complément du numéro de voie"}},
        default="",
    )
    lieu_dit = Column(
        String(38),
        info={"colanderalchemy": {"title": "Lieu-dit"}},
        default="",
    )
    # Informations sur la naissance
    birth_name = Column(
        String(80),
        info={
            "colanderalchemy": {
                "title": "Nom de naissance",
                "description": "À renseigner s’il est différent du nom de famille",
            }
        },
        default="",
    )
    birthdate = Column(Date(), info={"colanderalchemy": {"title": "Date de naissance"}})
    # Lieu de naissance
    # InputLieuNaissanceDTO
    birthplace_city = Column(
        String(50), info={"colanderalchemy": {"title": "Commune de naissance"}}
    )
    birthplace_city_code = Column(
        String(5),
        info={
            "colanderalchemy": {
                "title": "Code INSEE",
                "description": "Code INSEE de la commune de naissance (renseigné "
                "automatiquement d’après les informations précédentes)",
            }
        },
        default="",
    )
    birthplace_department_code = Column(
        String(3),
        info={"colanderalchemy": {"title": "Département de naissance"}},
        default="",
    )
    birthplace_country_code = Column(
        String(5),
        default="99100",
        info={"colanderalchemy": {"title": "Pays de naissance"}},
    )
    # Banque
    # BIC
    # 11 caractères max
    # ^[a-zA-Z]{6}[0-9a-zA-Z]{2}([0-9a-zA-Z]{3})?$
    bank_account_bic = Column(
        String(12),
        info={
            "colanderalchemy": {
                "title": "BIC",
                "description": "BIC du compte bancaire",
            }
        },
    )
    # IBAN
    # 34 caractères max :
    # ^[a-zA-Z]{2}[0-9]{2}[a-zA-Z0-9]{4}[0-9]{7}([a-zA-Z0-9]?){0,16}$
    bank_account_iban = Column(
        String(35),
        info={
            "colanderalchemy": {
                "title": "IBAN",
                "description": "IBAN du compte bancaire, sans espace entre les chiffres",
            }
        },
    )
    bank_account_owner = Column(
        String(100),
        info={
            "colanderalchemy": {
                "title": "Titulaire",
                "description": "Civilité, Nom et Prénom du titulaire du compte",
            }
        },
    )
    # Statut d'enregistrement auprès de l'ursaff
    registration_status = relationship(
        UrssafCustomerRegistrationStatus,
        back_populates="data",
        single_parent=True,
        uselist=False,
        cascade="all, delete-orphan",
        info={"colanderalchemy": {"exclude": True}},
    )

    def get_status(self) -> Optional[str]:
        if self.registration_status and self.registration_status.status != "disabled":
            return self.registration_status.status
        else:
            return None

    @property
    def birthplace_department(self):
        result = ""
        if self.birthplace_department_code:
            for item in DEPARTMENTS:
                if item["code_insee"] == self.birthplace_department_code:
                    result = item["name"]
                    break
        return result

    @property
    def birthplace_country(self):
        result = ""
        if self.birthplace_country_code:
            for item in COUNTRIES:
                if item["code_insee"] == self.birthplace_country_code:
                    result = item["name"]
                    break
        return result

    def __json__(self, request):
        return dict(
            id=self.id,
            client_id=self.client_id,
            customer_id=self.customer_id,
            street_type=self.street_type,
            street_name=self.street_name,
            street_number=self.street_number,
            street_number_complement=self.street_number_complement,
            lieu_dit=self.lieu_dit,
            birth_name=self.birth_name,
            birthdate=self.birthdate,
            birthplace_city=self.birthplace_city,
            birthplace_city_code=self.birthplace_city_code,
            birthplace_department_code=self.birthplace_department_code,
            birthplace_country_code=self.birthplace_country_code,
        )

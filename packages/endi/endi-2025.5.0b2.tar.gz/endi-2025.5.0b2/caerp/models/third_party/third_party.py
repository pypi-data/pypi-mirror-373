"""
    ThirdParty model
"""

import logging

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    ForeignKey,
)
from sqlalchemy.orm import (
    deferred,
    relationship,
)
from sqlalchemy.event import listen, remove

from caerp_base.models.base import (
    default_table_args,
    DBSESSION,
)
from caerp.models.config import Config
from caerp.models.node import Node
from caerp.models.listeners import SQLAListeners
from caerp.models.company import Company
from caerp.utils.compat import Iterable

from .services.third_party import ThirdPartyService
from ..status import (
    status_history_relationship,
    StatusLogEntry,
)


log = logging.getLogger(__name__)


class ThirdParty(Node):
    """
    Metadata pour un tiers (client, fournisseur)
    """

    __tablename__ = "third_party"
    __table_args__ = default_table_args
    __mapper_args__ = {"polymorphic_identity": "third_party"}
    _caerp_service = ThirdPartyService

    id = Column(
        Integer,
        ForeignKey("node.id"),
        primary_key=True,
        info={"colanderalchemy": {"exclude": True}},
    )
    company_id = Column(
        "company_id",
        Integer,
        ForeignKey("company.id"),
        info={
            "export": {"exclude": True},
            "colanderalchemy": {"exclude": True},
        },
        nullable=False,
    )
    source_company_id = Column(
        "source_company_id",
        Integer,
        ForeignKey("company.id", ondelete="SET NULL"),
        info={
            "export": {"exclude": True},
            "colanderalchemy": {"exclude": True},
        },
        nullable=True,
    )
    statuses = status_history_relationship()

    # Type company/individual/internal
    type = Column(
        "type",
        String(10),
        default="company",
        info={
            "colanderalchemy": {
                "title": "Type de client",
            },
            "export": {"label": "Type de client"},
        },
    )
    code = Column(
        "code",
        String(4),
        info={
            "colanderalchemy": {
                "title": "Code",
                "description": "Codification interne (ne figure pas dans les documents)",
            }
        },
    )
    # Label utilisé dans l'interface, mis à jour en fonction du type
    label = Column(
        "label",
        String(255),
        info={
            "colanderalchemy": {"exclude": True},
        },
        default="",
    )
    # Spécifique aux types company et internal : nom de la personne morale
    company_name = Column(
        "company_name",
        String(255),
        info={
            "colanderalchemy": {
                "title": "Raison sociale",
            },
        },
        default="",
    )
    civilite = deferred(
        Column(
            "civilite",
            String(10),
            info={
                "colanderalchemy": {
                    "title": "Civilité",
                }
            },
            default="",
        ),
        group="edit",
    )
    lastname = deferred(
        Column(
            "lastname",
            String(255),
            info={
                "colanderalchemy": {
                    "title": "Nom",
                }
            },
            default="",
        ),
        group="edit",
    )
    firstname = deferred(
        Column(
            "firstname",
            String(255),
            info={
                "colanderalchemy": {
                    "title": "Prénom",
                }
            },
            default="",
        ),
        group="edit",
    )
    function = deferred(
        Column(
            "function",
            String(255),
            info={
                "colanderalchemy": {
                    "title": "Fonction",
                }
            },
            default="",
        ),
        group="edit",
    )
    registration = deferred(
        Column(
            "registration",
            String(255),
            info={
                "colanderalchemy": {
                    "title": "Numéro d'immatriculation",
                }
            },
            default="",
        ),
        group="edit",
    )
    address = deferred(
        Column(
            "address",
            String(255),
            info={
                "colanderalchemy": {
                    "title": "Adresse",
                }
            },
            default="",
        ),
        group="edit",
    )
    additional_address = deferred(
        Column(
            String(255),
            info={
                "colanderalchemy": {
                    "title": "Complément d'adresse",
                }
            },
            default="",
        ),
        group="edit",
    )
    zip_code = deferred(
        Column(
            "zip_code",
            String(20),
            info={
                "colanderalchemy": {
                    "title": "Code postal",
                },
            },
            default="",
        ),
        group="edit",
    )
    city = deferred(
        Column(
            "city",
            String(255),
            info={
                "colanderalchemy": {
                    "title": "Ville",
                }
            },
            default="",
        ),
        group="edit",
    )
    city_code = deferred(
        Column(
            String(8),
            info={
                "colanderalchemy": {
                    "title": "Code INSEE",
                    "description": "Code INSEE de la commune (renseigné automatiquement d’après les informations ci-dessus)",
                }
            },
            default="",
        ),
        group="edit",
    )
    country = deferred(
        Column(
            "country",
            String(150),
            info={
                "colanderalchemy": {"title": "Pays"},
            },
            default="FRANCE",
        ),
        group="edit",
    )
    country_code = deferred(
        Column(
            String(8),
            info={
                "colanderalchemy": {"title": "Code INSEE du Pays"},
            },
            default="99100",  # France
        ),
        group="edit",
    )
    email = deferred(
        Column(
            "email",
            String(255),
            info={
                "colanderalchemy": {
                    "title": "Adresse e-mail",
                },
            },
            default="",
        ),
        group="edit",
    )
    mobile = deferred(
        Column(
            "mobile",
            String(20),
            info={
                "colanderalchemy": {
                    "title": "Téléphone portable",
                },
            },
            default="",
        ),
        group="edit",
    )
    phone = deferred(
        Column(
            "phone",
            String(50),
            info={
                "colanderalchemy": {
                    "title": "Téléphone fixe",
                },
            },
            default="",
        ),
        group="edit",
    )
    fax = deferred(
        Column(
            "fax",
            String(50),
            info={
                "colanderalchemy": {
                    "title": "Fax",
                }
            },
            default="",
        ),
        group="edit",
    )
    tva_intracomm = deferred(
        Column(
            "tva_intracomm",
            String(50),
            info={
                "colanderalchemy": {"title": "TVA intracommunautaire"},
            },
            default="",
        ),
        group="edit",
    )
    compte_cg = deferred(
        Column(
            String(125),
            info={
                "colanderalchemy": {
                    "title": "Compte CG",
                },
            },
            default="",
        ),
        group="edit",
    )
    compte_tiers = deferred(
        Column(
            String(125),
            info={
                "colanderalchemy": {
                    "title": "Compte tiers",
                },
            },
            default="",
        ),
        group="edit",
    )
    archived = Column(
        Boolean(),
        default=False,
        info={"colanderalchemy": {"exclude": True, "title": "Archivé ?"}},
    )

    bank_account_bic = Column(
        String(12),
        info={
            "colanderalchemy": {
                "title": "BIC",
                "description": "BIC du compte bancaire",
            }
        },
    )
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

    source_company = relationship(
        "Company",
        primaryjoin="Company.id==ThirdParty.source_company_id",
        info={
            "colanderalchemy": {"exclude": True},
            "export": {"exclude": True},
        },
    )

    @classmethod
    def from_company(
        cls, source_company: "Company", owner_company: "Company"
    ) -> "ThirdParty":
        """
        Build up a Third party instance from a company
        :param obj source_company: The company we want to create a ThirdParty
        from
        :param obj owner_company: Which company the ThirdParty belongs to

        :returns: A new ThirdParty instance
        """
        query = cls.query().filter_by(
            source_company_id=source_company.id, company_id=owner_company.id
        )
        edit = False
        if query.count() > 0:
            model = query.first()
            model.archived = False
            edit = True
        else:
            model = cls(type="internal")
            model.company_name = source_company.name
        model.source_company_id = source_company.id

        # Si on a bien un seul employé actif on l'utilise comme contact
        active_employees = source_company.get_active_employees()
        if len(active_employees) == 0:
            raise Exception("No active employee")
        if len(active_employees) == 1:
            model.lastname = active_employees[0].lastname
            model.firstname = active_employees[0].firstname
            model.civilite = active_employees[0].civilite

        model.email = source_company.email
        model.address = Config.get_value("cae_address")
        model.zip_code = Config.get_value("cae_zipcode")
        model.city = Config.get_value("cae_city")
        model.company_id = owner_company.id
        model.label = model._get_label()
        if edit:
            DBSESSION().merge(model)
            DBSESSION().flush()
        else:
            DBSESSION().add(model)
            DBSESSION().flush()
        return model

    def get_company_id(self):
        """
        :returns: the id of the company this third_party belongs to
        """
        return self.company.id

    def extra_statuses(self) -> Iterable[StatusLogEntry]:
        # Node children contribute to my history
        # Used for eg in sap_urssaf3p plugin to provide registration status
        for child in self.children:
            yield from child.statuses

    def __json__(self, request):
        """
        :returns: a dict version of the third_party object
        """
        return dict(
            id=self.id,
            created_at=self.created_at.isoformat(),
            updated_at=self.updated_at.isoformat(),
            company_id=self.company_id,
            type=self.type,
            code=self.code,
            label=self.label,
            company_name=self.company_name,
            civilite=self.civilite,
            lastname=self.lastname,
            firstname=self.firstname,
            function=self.function,
            registration=self.registration,
            address=self.address,
            additional_address=self.additional_address,
            zip_code=self.zip_code,
            city=self.city,
            city_code=self.city_code,
            country=self.country,
            country_code=self.country_code,
            full_address=self.full_address,
            email=self.email,
            mobile=self.mobile,
            phone=self.phone,
            fax=self.fax,
            tva_intracomm=self.tva_intracomm,
            compte_cg=self.compte_cg,
            compte_tiers=self.compte_tiers,
            archived=self.archived,
            status_history=[
                status.__json__(request)
                for status in self.get_allowed_statuses(request)
            ],
        )

    @property
    def full_address(self):
        """
        Return the third_party address formatted in french format
        """
        return self._caerp_service.get_address(self)

    def is_deletable(self):
        """
        Return True if this third_party could be deleted
        """
        return self.archived

    def is_company(self):
        """
        Return True if this third_party is a company
        """
        return self.type == "company"

    def is_internal(self):
        return self.type == "internal"

    def _get_label(self):
        return self._caerp_service.get_label(self)

    def get_name(self):
        return self._caerp_service.format_name(self)

    @classmethod
    def label_query(cls):
        return cls._caerp_service.label_query(cls)

    def get_general_account(self, prefix=""):
        return self._caerp_service.get_general_account(self, prefix)

    def get_third_party_account(self, prefix=""):
        return self._caerp_service.get_third_party_account(self, prefix)

    @classmethod
    def get_by_label(cls, label: str, company: "Company", case_sensitive: bool = False):
        return cls._caerp_service.get_by_label(cls, label, company, case_sensitive)


def set_third_party_label(mapper, connection, target):
    """
    Set the label of the given third_party
    """
    target.label = target._get_label()
    target.name = target.label


def start_listening():
    listen(ThirdParty, "before_insert", set_third_party_label, propagate=True)
    listen(ThirdParty, "before_update", set_third_party_label, propagate=True)


def stop_listening():
    remove(ThirdParty, "before_insert", set_third_party_label)
    remove(ThirdParty, "before_update", set_third_party_label)


SQLAListeners.register(start_listening, stop_listening)

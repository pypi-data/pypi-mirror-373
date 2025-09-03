"""
    Company model
"""
import logging

from sqlalchemy import (
    Table,
    Column,
    Integer,
    Numeric,
    String,
    Text,
    ForeignKey,
    Date,
    Boolean,
    Float,
)
from sqlalchemy.orm import (
    relationship,
    deferred,
    backref,
)

from caerp_base.models.base import (
    DBBASE,
    DBSESSION,
    default_table_args,
)

from caerp.compute import math_utils
from caerp.models.node import Node
from caerp.models.options import (
    ConfigurableOption,
    get_id_foreignkey_col,
)
from caerp.models.tools import (
    get_excluded_colanderalchemy,
)
from caerp.models.services.company import CompanyService
from caerp.models.user.user import COMPANY_EMPLOYEE

log = logging.getLogger(__name__)


COMPANY_ACTIVITY = Table(
    "company_activity_rel",
    DBBASE.metadata,
    Column(
        "company_id",
        ForeignKey("company.id", ondelete="CASCADE"),
    ),
    Column("activity_id", ForeignKey("company_activity.id", ondelete="CASCADE")),
    mysql_charset=default_table_args["mysql_charset"],
    mysql_engine=default_table_args["mysql_engine"],
)


class CompanyActivity(ConfigurableOption):
    """
    Company activities
    """

    __colanderalchemy_config__ = {
        "title": "Domaine d'activité",
        "validation_msg": "Les domaines d'activité ont bien été configurées",
    }
    id = get_id_foreignkey_col("configurable_option.id")


class Company(Node):
    """
    Company model
    Store all company specific stuff (headers, logos, RIB, ...)
    """

    __tablename__ = "company"
    __table_args__ = default_table_args
    __mapper_args__ = {"polymorphic_identity": "company"}
    # Meta informations
    id = Column(
        ForeignKey("node.id"),
        primary_key=True,
        info={"colanderalchemy": {"exclude": True}},
    )

    active = deferred(Column(Boolean(), default=True))

    # Informations générales
    # FIXME : pas utilisé
    goal = deferred(
        Column(
            "object",
            String(255),
            default="",
            info={
                "colanderalchemy": {
                    "title": "Descriptif de l'activité",
                },
            },
        ),
        group="edit",
    )
    email = deferred(
        Column(
            "email",
            String(255),
            info=dict(colanderalchemy=dict(title="E-mail")),
        ),
        group="edit",
    )
    phone = deferred(
        Column(
            "phone",
            String(20),
            default="",
            info=dict(
                colanderalchemy=dict(
                    title="Téléphone",
                )
            ),
        ),
        group="edit",
    )
    mobile = deferred(
        Column(
            "mobile",
            String(20),
            info=dict(
                colanderalchemy=dict(
                    title="Téléphone mobile",
                )
            ),
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
    country = deferred(
        Column(
            "country",
            String(150),
            info={
                "colanderalchemy": {
                    "title": "Pays",
                },
            },
            default="France",
        ),
        group="edit",
    )

    latitude = deferred(
        Column(
            "latitude",
            Float,
            nullable=True,
        ),
        group="edit",
    )

    longitude = deferred(
        Column(
            "longitude",
            Float,
            nullable=True,
        ),
        group="edit",
    )

    # Personnalisation des documents
    decimal_to_display = deferred(
        Column(
            Integer,
            default=2,
            info={
                "colanderalchemy": {
                    "title": "Nombre de décimales à afficher dans les sous-totaux",
                    "description": "Pour les prix unitaires et les sous-totaux HT, Indiquez le nombre de décimales à afficher.",
                }
            },
        ),
        group="edit",
    )

    logo_id = Column(
        ForeignKey("file.id"),
        info={
            # "colanderalchemy": {"exclude": True},
            "colanderalchemy": dict(
                title="Choisir un logo",
                description=(
                    "Ce logo n’est affiché dans vos documents (devis, factures…) que si aucun"
                    " En-tête des fichiers PDF n’est renseigné dans la rubrique"
                    " Personnalisation des documents ci-dessous.  "
                ),
            ),
            "export": {"exclude": True},
        },
    )

    header_id = Column(
        ForeignKey("file.id"),
        info={
            # "colanderalchemy": {"exclude": True},
            "colanderalchemy": dict(
                title="En-tête des fichiers PDF",
                description=(
                    "Le fichier est idéalement au format 5/1 (par exemple 1000px x 200 px)."
                    " Remplace l’en-tête par défaut qui utilise les informations publiques."
                    " Consulter la <a title='Ouvrir la documentation dans une nouvelle fenêtre'"
                    " aria-label='Ouvrir la documentation dans une nouvelle fenêtre'"
                    " href='https://doc.endi.coop/#Banniere_Creer'"
                    " target='_blank'>documentation</a> pour obtenir un modèle et plus"
                    " d'informations."
                ),
            ),
            "export": {"exclude": True},
        },
    )
    cgv = deferred(
        Column(
            Text,
            default="",
            info=dict(
                colanderalchemy=dict(
                    title="Conditions générales complémentaires",
                ),
            ),
        ),
        group="edit",
    )
    # Paramètres techniques
    internal = Column(
        Boolean(),
        default=False,
        nullable=False,
        info=dict(
            colanderalchemy=dict(
                title="Enseigne interne à la CAE",
                description="""
            À cocher si l'enseigne est utilisé pour abriter l'activité
            interne à la CAE, par opposition avec l'activité des entrepreneurs.
            Vous pouvez aussi configurer les enseignes internes dans
            Configuration → Configuration Générale →
            Enseigne(s) interne(s) à la CAE.
        """,
            ),
        ),
    )
    RIB = deferred(
        Column(
            "RIB",
            String(255),
            info=dict(
                colanderalchemy=dict(
                    title="RIB",
                )
            ),
        ),
        group="edit",
    )
    IBAN = deferred(
        Column(
            "IBAN",
            String(255),
            info=dict(
                colanderalchemy=dict(
                    title="IBAN",
                )
            ),
        ),
        group="edit",
    )

    code_compta = deferred(
        Column(
            String(30),
            default="",
            info=dict(
                colanderalchemy=dict(
                    title="Compte analytique",
                    description=(
                        "Compte analytique utilisé dans le logiciel de comptabilité"
                    ),
                ),
            ),
        ),
        group="edit",
    )

    general_customer_account = deferred(
        Column(
            String(255),
            default="",
            info=dict(
                colanderalchemy=dict(
                    title="Compte client général",
                    description=(
                        "Laisser vide pour utiliser les paramètres de la "
                        "configuration générale"
                    ),
                )
            ),
        ),
        group="edit",
    )

    general_expense_account = deferred(
        Column(
            String(255),
            default="",
            info=dict(
                colanderalchemy=dict(
                    title=(
                        "Compte général (classe 4) pour les dépenses dues aux"
                        " entrepreneurs"
                    ),
                    description=(
                        "Concerne notes de dépense et l'éventuelle part"
                        " entrepreneur des factures fournisseur. Laisser vide"
                        " pour utiliser les paramètres de la configuration"
                        " générale"
                    ),
                )
            ),
        ),
        group="edit",
    )

    third_party_customer_account = deferred(
        Column(
            String(255),
            default="",
            info=dict(
                colanderalchemy=dict(
                    title="Compte client tiers",
                    description=(
                        "Laisser vide pour utiliser les paramètres de la "
                        "configuration générale"
                    ),
                )
            ),
        ),
        group="edit",
    )

    general_supplier_account = deferred(
        Column(
            String(255),
            default="",
            info=dict(
                colanderalchemy=dict(
                    title="Compte fournisseur général",
                    description=(
                        "Laisser vide pour utiliser les paramètres de la "
                        "configuration générale"
                    ),
                )
            ),
        ),
        group="edit",
    )

    third_party_supplier_account = deferred(
        Column(
            String(255),
            default="",
            info=dict(
                colanderalchemy=dict(
                    title="Compte fournisseur tiers",
                    description=(
                        "Laisser vide pour utiliser les paramètres de la "
                        "configuration générale"
                    ),
                )
            ),
        ),
        group="edit",
    )
    internalgeneral_customer_account = deferred(
        Column(
            String(255),
            default="",
            info=dict(
                colanderalchemy=dict(
                    title="Compte client général pour les clients internes",
                    description=(
                        "Laisser vide pour utiliser les paramètres de la "
                        "configuration générale"
                        ""
                    ),
                )
            ),
        ),
        group="edit",
    )

    internalthird_party_customer_account = deferred(
        Column(
            String(255),
            default="",
            info=dict(
                colanderalchemy=dict(
                    title="Compte client tiers pour les clients internes",
                    description=(
                        "Laisser vide pour utiliser les paramètres de la "
                        "configuration générale"
                    ),
                )
            ),
        ),
        group="edit",
    )

    internalgeneral_supplier_account = deferred(
        Column(
            String(255),
            default="",
            info=dict(
                colanderalchemy=dict(
                    title="Compte fournisseur général pour les fournisseurs internes",
                    description=(
                        "Laisser vide pour utiliser les paramètres de la "
                        "configuration générale"
                    ),
                ),
            ),
        ),
        group="edit",
    )

    internalthird_party_supplier_account = deferred(
        Column(
            String(255),
            default="",
            info=dict(
                colanderalchemy=dict(
                    title="Compte fournisseur tiers pour les fournisseurs internes",
                    description=(
                        "Laisser vide pour utiliser les paramètres de la "
                        "configuration générale"
                    ),
                ),
            ),
        ),
        group="edit",
    )

    default_add_estimation_details_in_invoice = deferred(
        Column(
            Boolean(),
            default=None,
            info=dict(
                colanderalchemy=dict(
                    title=(
                        "Ajouter les détails du devis dans les factures d'acompte "
                        "et intermédiaire"
                    ),
                    description=(
                        "Si coché, par défaut, les détails des lignes du devis "
                        "d'origine sont ajoutés dans les factures d'acompte et"
                        " intermédiaire"
                    ),
                ),
            ),
        ),
        group="edit",
    )
    default_estimation_deposit = deferred(
        Column(
            Integer,
            default=0,
            info=dict(
                colanderalchemy=dict(
                    title="Acompte par défaut",
                    description="Acompte par défaut à appliquer sur les devis "
                    " (vide = 0%)",
                ),
            ),
        ),
        group="edit",
    )

    # FIXME : pas sûr que cet attribut soit utilisé, à investiguer
    bank_account = deferred(
        Column(
            String(255),
            default="",
        ),
        group="edit",
    )
    # Taux de contribution et d'assurance "custom" par enseigne
    insurance = deferred(
        Column(
            Numeric(5, 2, asdecimal=False),
            info=dict(
                colanderalchemy=dict(
                    title="Taux d'assurance professionnelle",
                    description="Taux d'assurance à utiliser pour cette enseigne",
                ),
            ),
        ),
        group="edit",
    )
    internalinsurance = deferred(
        Column(
            Numeric(5, 2, asdecimal=False),
            info=dict(
                colanderalchemy=dict(
                    title=(
                        "Taux d'assurance professionnelle pour la facturation interne"
                    ),
                    description=(
                        "Taux d'assurance à utiliser pour cette enseigne"
                        " lorsqu'elle facture en interne"
                    ),
                ),
            ),
        ),
        group="edit",
    )
    contribution = deferred(
        Column(
            Numeric(5, 2, asdecimal=False),
            info=dict(
                colanderalchemy=dict(
                    title="Contribution à la CAE",
                    description=(
                        "Pourcentage que cette enseigne contribue à la CAE. Utilisé"
                        " pour les écritures et dans les calculs de coût de revient"
                        " (catalogue/étude de prix)"
                    ),
                ),
            ),
        ),
        group="edit",
    )
    internalcontribution = deferred(
        Column(
            Numeric(5, 2, asdecimal=False),
            info=dict(
                colanderalchemy=dict(
                    title="Contribution à la CAE pour la facturation interne",
                    description=(
                        "Pourcentage que cette enseigne contribue à la CAE"
                        " lorsqu’elle facture en interne"
                    ),
                ),
            ),
        ),
        group="edit",
    )
    # Coefficients de calcul pour les études de prix
    general_overhead = deferred(
        Column(
            Numeric(
                6,
                5,
                asdecimal=False,
            ),
            info=dict(
                colanderalchemy=dict(
                    title="Coefficient de frais généraux",
                    description="""
        Coefficient de frais généraux utilisé par défaut dans les études de prix pour
        le calcul du prix de vente depuis le coût d'achat.
        Doit être compris entre 0 et 10.
        """,
                )
            ),
            default=0,
        ),
        group="edit",
    )
    margin_rate = deferred(
        Column(
            Numeric(6, 5, asdecimal=False),
            default=0,
            info=dict(
                colanderalchemy=dict(
                    title="Coefficient de marge",
                    description="""
        Coefficient de marge utilisé par défaut dans les études de prix et le catalogue
        produit pour le calcul du prix de vente depuis le coût d'achat.
        Doit être compris entre 0 et 1.""",
                ),
            ),
        ),
        group="edit",
    )
    use_margin_rate_in_catalog = deferred(
        Column(
            Boolean(),
            default=False,
            info=dict(
                colanderalchemy=dict(
                    title="Coefficient de marge dans le catalogue ?",
                    label="Coefficient de marge dans le catalogue",
                    description="""
        Le coefficient de marge appliqué aux produits peut-il être dans le catalogue
        (ou seulement au moment de l'étude de prix)?
        """,
                ),
            ),
        )
    )

    # sequences related, used for counters initialization on migration from
    # another system (eg: WinScop). Contain the latest index already assigned.
    month_company_invoice_sequence_init_value = deferred(
        Column(Integer, info={"colanderalchemy": {"exclude": True}}),
    )

    month_company_invoice_sequence_init_date = deferred(
        Column(
            Date,
            info={
                "colanderalchemy": {"exclude": True},
            },
        ),
    )

    antenne_id = deferred(
        Column(
            ForeignKey("antenne_option.id", ondelete="set null"),
            info=dict(
                colanderalchemy=dict(
                    title="Antenne de rattachement",
                )
            ),
        )
    )

    follower_id = deferred(
        Column(
            ForeignKey("accounts.id", ondelete="set null"),
            info=dict(
                colanderalchemy=dict(
                    title="Accompagnateur de l'enseigne",
                    ondelete="set null",
                )
            ),
        )
    )
    smtp_configuration = Column(
        String(8),  # (no, cae, company)
        default="none",
        info={
            "colanderalchemy": {
                "title": "",
            }
        },
    )

    # Relationships
    follower = relationship(
        "User",
        primaryjoin="User.id==Company.follower_id",
        info={
            "colanderalchemy": {"exclude": True},
            "export": {"exclude": True},
        },
    )

    antenne = relationship(
        "AntenneOption",
        info={
            "colanderalchemy": {"exclude": True},
            "export": {"exclude": True},
        },
    )

    header_file = relationship(
        "File",
        primaryjoin="File.id==Company.header_id",
        # backref utilisé pour le calcul des acls
        back_populates="company_header_backref",
        info={
            "colanderalchemy": {"exclude": True},
            "export": {"exclude": True},
        },
    )

    logo_file = relationship(
        "File",
        primaryjoin="File.id==Company.logo_id",
        # backref utilisé pour le calcul des acls
        back_populates="company_logo_backref",
        uselist=False,
        info={
            "colanderalchemy": {"exclude": True},
            "export": {"exclude": True},
        },
    )

    activities = relationship(
        "CompanyActivity",
        secondary=COMPANY_ACTIVITY,
        backref=backref(
            "companies",
            info={
                "colanderalchemy": {"exclude": True},
                "export": {"exclude": True},
            },
        ),
        info={
            "colanderalchemy": {
                "title": "Domaines d'activités",
            },
            "export": {"exclude": True},
        },
    )

    customers = relationship(
        "Customer",
        primaryjoin="Company.id==Customer.company_id",
        order_by="Customer.code",
        back_populates="company",
        info={
            "colanderalchemy": {"exclude": True},
            "export": {"exclude": True},
        },
    )

    suppliers = relationship(
        "Supplier",
        order_by="Supplier.code",
        primaryjoin="Company.id==Supplier.company_id",
        back_populates="company",
        info={
            "colanderalchemy": {"exclude": True},
            "export": {"exclude": True},
        },
    )

    projects = relationship(
        "Project",
        primaryjoin="Project.company_id==Company.id",
        order_by="Project.id",
        back_populates="company",
        info={
            "colanderalchemy": {"exclude": True},
            "export": {"exclude": True},
        },
    )
    tasks = relationship(
        "Task",
        primaryjoin="Task.company_id==Company.id",
        order_by="Task.date",
        back_populates="company",
        info={
            "colanderalchemy": {"exclude": True},
            "export": {"exclude": True},
        },
    )
    employees = relationship(
        "User",
        secondary=COMPANY_EMPLOYEE,
        back_populates="companies",
        info={
            "colanderalchemy": get_excluded_colanderalchemy("Employés"),
            "export": {"exclude": True},
        },
    )
    sale_products = relationship(
        "BaseSaleProduct",
        order_by="BaseSaleProduct.label",
        back_populates="company",
        info={
            "colanderalchemy": {"exclude": True},
            "export": {"exclude": True},
        },
    )
    expense = relationship(
        "ExpenseSheet",
        primaryjoin="ExpenseSheet.company_id==Company.id",
        order_by="ExpenseSheet.month",
        cascade="all, delete-orphan",
        back_populates="company",
        info={
            "colanderalchemy": {"exclude": True},
            "export": {"exclude": True},
        },
    )
    supplier_invoices = relationship(
        "SupplierInvoice",
        primaryjoin="SupplierInvoice.company_id==Company.id",
        order_by="SupplierInvoice.date",
        back_populates="company",
        info={
            "colanderalchemy": {"exclude": True},
            "export": {"exclude": True},
        },
    )

    _caerp_service = CompanyService

    def get_company_id(self):
        """
        Return the current company id
        Allows company id access through request's context
        """
        return self.id

    @property
    def header(self):
        return self.header_file

    @header.setter
    def header(self, appstruct):
        self._set_company_image(appstruct, "header_file", "header.png")

    @property
    def logo(self):
        return self.logo_file

    @logo.setter
    def logo(self, appstruct):
        self._set_company_image(appstruct, "logo_file", "logo.png")

    def _set_company_image(
        self,
        appstruct: dict,
        image_attr_name: str = "logo_file",
        default_name: str = "logo.png",
    ):
        image_attr = getattr(self, image_attr_name)
        if image_attr is not None and appstruct.get("delete"):
            DBSESSION().delete(image_attr)
        else:
            filename = appstruct.get("filename", default_name)
            if image_attr is None:
                from caerp.models.files import File

                image_attr = File()

            image_attr.name = filename
            image_attr.description = image_attr_name
            image_attr.mimetype = appstruct.get("mimetype", "image/png")
            image_attr.size = appstruct.get("size", None)
            if appstruct.get("fp"):
                image_attr.data = appstruct["fp"]
            setattr(self, image_attr_name, image_attr)

    @property
    def full_label(self):
        """
        Return the company's label to display

        Add employees infos to company's name if config ask to
        """
        return self.format_label_from_datas(self)

    @property
    def main_activity(self):
        """
        Return the company's main activity
        (first 'company_activity_rel' entry)
        """
        return self.get_main_activity()

    @classmethod
    def query(cls, keys=None, active=True):
        """
        Return a query
        """
        if keys:
            query = DBSESSION().query(*keys)
        else:
            query = super(Company, cls).query()
        if active:
            query = query.filter(cls.active == True)  # noqa: E712
        return query.order_by(cls.name)

    def __json__(self, request):
        """
        return a dict representation
        """
        customers = [customer.__json__(request) for customer in self.customers]
        suppliers = [supplier.__json__(request) for supplier in self.suppliers]
        projects = [project.__json__(request) for project in self.projects]

        return dict(
            id=self.id,
            name=self.name,
            goal=self.goal,
            email=self.email,
            phone=self.phone,
            mobile=self.mobile,
            latitude=self.latitude,
            longitude=self.longitude,
            RIB=self.RIB,
            IBAN=self.IBAN,
            customers=customers,
            suppliers=suppliers,
            projects=projects,
            status_history=[
                status.__json__(request)
                for status in self.get_allowed_statuses(request)
            ],
        )

    def disable(self):
        """
        Disable the current company
        """
        self.active = False

    def enable(self):
        """
        enable the current company
        """
        self.active = True

    def get_tasks(self):
        """
        Get all tasks for this company, as a list
        """
        return self._caerp_service.get_tasks(self)

    def get_recent_tasks(self, page_nb, nb_per_page):
        """
        :param int nb_per_page: how many to return
        :param int page_nb: pagination index

        .. todo:: this is naive, use sqlalchemy pagination

        :return: pagination for wanted tasks, total nb of tasks
        """
        count = self.get_tasks().count()
        offset = page_nb * nb_per_page
        items = self._caerp_service.get_tasks(self, offset=offset, limit=nb_per_page)
        return items, count

    def get_estimations(self, valid=False):
        """
        Return the estimations of the current company
        """
        return self._caerp_service.get_estimations(self, valid)

    def get_invoices(self, valid=False):
        """
        Return the invoices of the current company
        """
        return self._caerp_service.get_invoices(self, valid)

    def get_cancelinvoices(self, valid=False):
        """
        Return the cancelinvoices of the current company
        """
        return self._caerp_service.get_cancelinvoices(self, valid)

    def has_invoices(self):
        """
        return True if this company owns invoices
        """
        return (
            self.get_invoices(self, valid=True).count() > 0
            or self.get_cancelinvoices(self, valid=True).count() > 0
        )

    def has_visible_businesses(self):
        """
        Return if the company has at least one visible business
        """
        for project in self.projects:
            for business in project.businesses:
                if business.visible:
                    return True
        return False

    def get_real_customers(self, year):
        """
        Return the real customers (with invoices)
        """
        return self._caerp_service.get_customers(self, year)

    def get_late_invoices(self):
        """
        Return invoices waiting for more than 45 days
        """
        return self._caerp_service.get_late_invoices(self)

    def get_customer_codes_and_names(self):
        """
        Return current company's customer codes and names
        """
        return self._caerp_service.get_customer_codes_and_names(self)

    def get_supplier_codes_and_names(self):
        """
        Return current company's supplier codes and names
        """
        return self._caerp_service.get_supplier_codes_and_names(self)

    def get_project_codes_and_names(self):
        """
        Return current company's project codes and names
        """
        return self._caerp_service.get_project_codes_and_names(self)

    def get_next_estimation_index(self):
        """
        Return the next estimation index
        """
        return self._caerp_service.get_next_estimation_index(self)

    def get_next_invoice_index(self):
        """
        Return the next invoice index
        """
        return self._caerp_service.get_next_invoice_index(self)

    def get_next_cancelinvoice_index(self):
        """
        Return the next cancelinvoice index
        """
        return self._caerp_service.get_next_cancelinvoice_index(self)

    def get_turnover(self, start_date, end_date):
        """
        Retrieve the turnover for the current company on the given period
        """
        ca = self._caerp_service.get_turnover(self, start_date, end_date)
        return math_utils.integer_to_amount(ca, precision=5)

    def get_total_expenses_on_period(self, start_date, end_date):
        """
        Retrieve the expense total HT for the current company on the given period
        """
        total_expenses = self._caerp_service.get_total_expenses_on_period(
            self, start_date, end_date
        )
        return math_utils.integer_to_amount(total_expenses, precision=2)

    def get_nb_km_on_period(self, start_date, end_date):
        """
        Retrieve the kilometers declared for the current company on the given period
        """
        return self._caerp_service.get_nb_km_on_period(self, start_date, end_date)

    def get_total_expenses_and_km_on_period(self, start_date, end_date):
        """
        Retrieve the expense total HT and the kilometers declared
        for the current company on the given period
        """
        total_expenses, nb_km = self._caerp_service.get_total_expenses_and_km_on_period(
            self, start_date, end_date
        )
        return math_utils.integer_to_amount(total_expenses, precision=2), nb_km

    def get_total_purchases_on_period(self, start_date, end_date):
        """
        Retrieve the purchase total HT for the current company on the given period
        """
        total_purchases = self._caerp_service.get_total_purchases_on_period(
            self, start_date, end_date
        )
        return math_utils.integer_to_amount(total_purchases, precision=2)

    def get_last_treasury_main_indicator(self):
        """
        Retrieve the main indicator's datas from the last treasury grid
        of a given company
        Return {"date", "label", "value"} of the measure
        """
        return self._caerp_service.get_last_treasury_main_indicator(self)

    def set_datas_from_user(self, user_account):
        if self.antenne_id == None and user_account.userdatas != None:
            self.antenne_id = user_account.userdatas.situation_antenne_id
        if self.follower_id == None and user_account.userdatas != None:
            self.follower_id = user_account.userdatas.situation_follower_id

    """
    @classmethod
    def label_query(cls):
        return cls._caerp_service.label_query(cls)

    @classmethod
    def query_for_select(cls, active_only=False):
        return cls._caerp_service.query_for_select(cls, active_only)
    """

    @classmethod
    def label_datas_query(cls, request, only_active=False):
        return cls._caerp_service.label_datas_query(cls, request, only_active)

    @classmethod
    def format_label_from_datas(cls, company_datas, with_select_search_datas=False):
        """
        company_datas:
            can be either an SqlAlchemy.Row : (
                id,
                name,
                code_compta,
                active,
                nb_employees,
                employees_list
            )
            or a dict : {
                'id': int,
                'name': str,
                'code_compta': str,
                'active': bool,
                'nb_employees': int,
                'employees_list': str
            }
        """
        return cls._caerp_service.format_label_from_datas(
            cls, company_datas, with_select_search_datas
        )

    @classmethod
    def get_companies_select_datas(cls, request, only_active=False):
        return cls._caerp_service.get_companies_select_datas(cls, request, only_active)

    @classmethod
    def get_id_by_analytical_account(cls, analytical_account):
        return cls._caerp_service.get_id_by_analytical_account(cls, analytical_account)

    @classmethod
    def get_companies_by_analytical_account(cls, analytical_account, active_only=False):
        return cls._caerp_service.get_companies_by_analytical_account(
            cls, analytical_account, active_only
        )

    @classmethod
    def query_for_select_with_trainer(cls, request):
        return cls._caerp_service.query_for_select_with_trainer(cls, request)

    def has_trainer(self):
        from caerp.consts.access_rights import ACCESS_RIGHTS

        return self.has_member_with_access_right(ACCESS_RIGHTS["es_trainer"]["name"])

    def get_employee_ids(self):
        return self._caerp_service.get_employee_ids(self)

    def get_active_employees(self):
        return self._caerp_service.get_active_employees(self)

    def has_member_with_access_right(self, access_right_name):
        return self._caerp_service.has_member_with_access_right(self, access_right_name)

    def employs(self, uid):
        """
        :param uiud int: User id
        """
        return self._caerp_service.employs(self, uid)

    @classmethod
    def get_contribution(cls, company_id, prefix=""):
        """
        :returns: The cae contribution percentage
        """
        return cls._caerp_service.get_contribution(company_id, prefix)

    @classmethod
    def get_rate(cls, company_id: int, rate_name: str, prefix: str = ""):
        """
        Récupère un taux à appliquer en fonction du nom du module
        d'écriture comptable concerné

        :param int company_id: L'id de l'enseigne
        :param str rate_name: Le nom du module d'écriture pour lequel on
        récupère le taux
        :param str prefix: préfixe de l'attribut à rechercher
        ('' ou 'internal')

        :rtype: float or None
        """
        return cls._caerp_service.get_rate(company_id, rate_name, prefix)

    @classmethod
    def get_rate_level(cls, company_id: int, rate_name: str, prefix: str = ""):
        """
        Renvoie le niveau (cae/company/document) auquel la contribution est
        définie

        :param int company_id: L'id de l'enseigne
        :param str rate_name: Le nom du module d'écriture pour lequel on
        récupère le taux
        :param str prefix: préfixe de l'attribut à rechercher
        ('' ou 'internal')

        :rtype: str or None
        """
        return cls._caerp_service.get_rate_level(company_id, rate_name, prefix)

    def get_general_customer_account(self, prefix=""):
        return self._caerp_service.get_general_customer_account(self, prefix)

    def get_third_party_customer_account(self, prefix=""):
        return self._caerp_service.get_third_party_customer_account(self, prefix)

    def get_general_supplier_account(self, prefix=""):
        return self._caerp_service.get_general_supplier_account(self, prefix)

    def get_third_party_supplier_account(self, prefix=""):
        return self._caerp_service.get_third_party_supplier_account(self, prefix)

    def get_general_expense_account(self, prefix=""):
        return self._caerp_service.get_general_expense_account(self, prefix)

    def get_main_activity(self):
        return self.activities[0].label if self.activities else ""

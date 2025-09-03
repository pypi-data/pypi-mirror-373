"""
    Task model
    represents a base task, with a status, an owner, a phase
"""

import datetime
import logging
from typing import Any, Dict

import colander
import deform
from caerp_base.models.base import DBBASE, DBSESSION, default_table_args
from caerp_base.models.mixins import OfficialNumberMixin
from sqlalchemy import (
    JSON,
    BigInteger,
    Boolean,
    Column,
    Date,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    desc,
    extract,
    func,
)
from sqlalchemy.dialects.mysql import DATETIME
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.orderinglist import ordering_list
from sqlalchemy.orm import backref, deferred, relationship, validates

from caerp.compute.math_utils import integer_to_amount
from caerp.compute.task import (
    DiscountLineCompute,
    DiscountLineTtcCompute,
    GroupCompute,
    GroupTtcCompute,
    LineCompute,
    LineTtcCompute,
    TaskCompute,
    TaskTtcCompute,
)
from caerp.models.config import Config
from caerp.models.export.accounting_export_log import (
    invoice_accounting_export_log_entry_association_table,
)
from caerp.models.node import Node
from caerp.models.services.naming import NamingService
from caerp.models.services.sale_file_requirements import TaskFileRequirementService
from caerp.models.task.mentions import MANDATORY_TASK_MENTION, TASK_MENTION
from caerp.models.tva import Product, Tva
from caerp.utils.strings import HOUR_UNITS, is_hours

from ..status import ValidationStatusHolderMixin
from .services import (
    DiscountLineService,
    PostTTCLineService,
    TaskLineGroupService,
    TaskLineService,
    TaskMentionService,
    TaskService,
)

logger = log = logging.getLogger(__name__)

ALL_STATES = ("draft", "wait", "valid", "invalid")


class FrozenSettingsModelMixin:
    """Allows to store/retrieve a frozen settings dict/list as JSON

    Could be used for something else than Task
    """

    def frozen_settings_initialize(self, frozen_settings) -> dict:
        raise NotImplementedError

    def freeze_settings(self):
        self.frozen_settings = self.frozen_settings_initialize()

    # attr should not be included in duplicate() to allow regeneration of
    # frozen_settings on
    frozen_settings = Column(
        JSON,
        default={},
        info={
            "export": {"exclude": True},
            "colanderalchemy": {"exclude": True},
        },
    )


class Task(
    FrozenSettingsModelMixin,
    OfficialNumberMixin,
    ValidationStatusHolderMixin,
    Node,
):
    """
    Metadata pour une tâche (estimation, invoice)
    """

    __tablename__ = "task"
    __table_args__ = default_table_args
    __mapper_args__ = {"polymorphic_identity": "task"}
    _caerp_service = TaskService
    file_requirement_service = TaskFileRequirementService
    mention_service = TaskMentionService
    naming_service = NamingService
    invoice_types = (
        "invoice",
        "cancelinvoice",
        "internalinvoice",
        "internalcancelinvoice",
    )
    estimation_types = ("estimation", "internalestimation")
    # Tags if the given class is dedicated to "internal" invoices and
    # estimations
    internal = False
    # Prefixes used to access configuration keys (at company or global level)
    prefix = ""

    id = Column(
        Integer,
        ForeignKey("node.id"),
        info={"export": {"exclude": True}},
        primary_key=True,
    )
    phase_id = Column(
        ForeignKey("phase.id"),
        info={"export": {"exclude": True}},
    )
    # Override status_date column type
    # Enable microseconds precision (instead of second)
    #
    # Allows the « export by invoice number range » feature…
    # … Which is in fact based on a sort on status_date column, and requires
    # predictable ordering, including for cases where two invoices have been
    # validated at the same second.
    status_date = Column(
        DATETIME(fsp=6),
        default=datetime.datetime.now,
        info={
            "colanderalchemy": {
                "title": "Date du dernier changement de statut",
            },
            "export": {"exclude": True},
        },
    )
    date = Column(
        Date(),
        info={"colanderalchemy": {"title": "Date du document"}},
        default=datetime.date.today,
    )
    owner_id = Column(
        ForeignKey("accounts.id"),
        info={
            "export": {"exclude": True},
        },
    )
    description = Column(
        Text,
        info={"colanderalchemy": {"title": "Objet"}},
    )
    # ttc or ht compute base
    mode = Column(
        String(10),
        info={
            "colanderalchemy": {"title": "Mode de saisie"},
            "export": {"exclude": True},
        },
        default="ht",
    )
    ht = Column(
        BigInteger(),
        info={
            "colanderalchemy": {"title": "Montant HT (cache)"},
            "export": {"exclude": True},
        },
        default=0,
    )
    tva = Column(
        BigInteger(),
        info={
            "colanderalchemy": {"title": "Montant TVA (cache)"},
            "export": {"exclude": True},
        },
        default=0,
    )
    ttc = Column(
        BigInteger(),
        info={
            "colanderalchemy": {"title": "Montant TTC (cache)"},
            "export": {"exclude": True},
        },
        default=0,
    )
    company_id = Column(
        Integer,
        ForeignKey("company.id"),
        nullable=False,
        info={
            "export": {"exclude": True},
        },
    )
    project_id = Column(
        Integer,
        ForeignKey("project.id"),
        nullable=False,
        info={
            "export": {"exclude": True},
        },
    )
    customer_id = Column(
        Integer,
        ForeignKey("customer.id"),
        nullable=False,
        info={
            "export": {"exclude": True},
        },
    )
    project_index = deferred(
        Column(
            Integer,
            info={
                "colanderalchemy": {
                    "title": "Index dans le dossier",
                },
                "export": {"exclude": True},
            },
        ),
        group="edit",
    )
    company_index = deferred(
        Column(
            Integer,
            info={
                "colanderalchemy": {
                    "title": "Index du document à l’échelle de l’enseigne",
                },
                "export": {"exclude": True},
            },
        ),
        group="edit",
    )
    official_number = Column(
        String(255),
        info={
            "colanderalchemy": {
                "title": "Identifiant du document (facture/avoir)",
            },
            "export": {"label": "Numéro de facture"},
        },
        default=None,
    )
    legacy_number = Column(
        Boolean,
        default=False,
        nullable=False,
        info={
            "export": {"exclude": True},
        },
    )
    internal_number = deferred(
        Column(
            String(255),
            default=None,
            info={
                "colanderalchemy": {
                    "title": "Identifiant du document dans la CAE",
                },
                "export": {"exclude": True},
            },
        ),
        group="edit",
    )
    display_units = deferred(
        Column(
            Integer,
            info={
                "colanderalchemy": {
                    "title": "Afficher le détail ?",
                    "validator": colander.OneOf((0, 1)),
                },
                "export": {"exclude": True},
            },
            default=0,
        ),
        group="edit",
    )
    display_ttc = deferred(
        Column(
            Integer,
            info={
                "colanderalchemy": {
                    "title": "Afficher les prix TTC ?",
                    "validator": colander.OneOf((0, 1)),
                },
                "export": {"exclude": True},
            },
            default=0,
        ),
        group="edit",
    )
    expenses_ht = deferred(
        Column(
            BigInteger(),
            info={
                "colanderalchemy": {"title": "Frais"},
                "export": {"exclude": True},
            },
            default=0,
        ),
        group="edit",
    )
    address = deferred(
        Column(
            Text,
            info={
                "colanderalchemy": {"title": "Adresse"},
                "export": {"exclude": True},
            },
        ),
        group="edit",
    )
    workplace = deferred(
        Column(
            Text,
            info={
                "colanderalchemy": {"title": "Lieu d’exécution"},
            },
        )
    )

    payment_conditions = deferred(
        Column(
            Text,
            info={
                "colanderalchemy": {
                    "title": "Conditions de paiement",
                },
                "export": {"exclude": True},
            },
        ),
        group="edit",
    )
    notes = deferred(
        Column(
            Text,
            info={
                "colanderalchemy": {"title": "Notes complémentaires"},
                "export": {"exclude": True},
            },
        ),
        group="edit",
    )
    round_floor = deferred(
        Column(
            Boolean(),
            default=False,
            info={
                "colanderalchemy": {
                    "exlude": True,
                    "title": "Méthode d’arrondi « à l’ancienne » ? (floor)",
                },
                "export": {"exclude": True},
            },
        ),
        group="edit",
    )
    # Nombre de décimal à afficher dans les documents
    decimal_to_display = deferred(Column(Integer, default=2), group="edit")
    business_type_id = Column(ForeignKey("business_type.id"), nullable=False)
    business_id = Column(
        ForeignKey("business.id"),
        info={"colanderalchemy": {"exclude": True}},
    )
    pdf_file_id = deferred(
        Column(ForeignKey("file.id"), info={"colanderalchemy": {"exclude": True}}),
        group="edit",
    )
    pdf_file_hash = deferred(
        Column(String(40), nullable=True),
        group="edit",
    )
    first_visit = Column(
        Date(),
        info={"colanderalchemy": {"title": "Date de première visite"}},
        nullable=True,
    )
    start_date = Column(
        Date(),
        info={"colanderalchemy": {"title": "Date de début des prestations"}},
        nullable=True,
    )
    # Date en string parce que ça peut être "première semaine après le début"
    end_date = deferred(
        Column(
            String(255),
            info={
                "colanderalchemy": {"title": "Date de fin de prestation"},
            },
        )
    )
    insurance_id = deferred(
        Column(ForeignKey("task_insurance_option.id")), group="edit"
    )
    # Mark task as autivalidated for filter purpose
    auto_validated = Column(
        Boolean(),
        default=False,
        info={
            "colanderalchemy": {"exclude": True},
            "export": {"exclude": True},
        },
    )

    # Organisationnal Relationships
    owner = relationship(
        "User",
        primaryjoin="Task.owner_id==User.id",
        backref=backref(
            "ownedTasks",
            info={
                "colanderalchemy": {"exclude": True},
                "export": {"exclude": True},
            },
        ),
        info={
            "colanderalchemy": {"exclude": True},
            "export": {"exclude": True},
        },
    )
    phase = relationship(
        "Phase",
        primaryjoin="Task.phase_id==Phase.id",
        backref=backref(
            "tasks",
            order_by="Task.date",
            info={
                "colanderalchemy": {"exclude": True},
                "export": {"exclude": True},
            },
        ),
        info={
            "colanderalchemy": {"exclude": True},
            "export": {"exclude": True},
        },
    )
    company = relationship(
        "Company",
        primaryjoin="Task.company_id==Company.id",
        info={
            "colanderalchemy": {"exclude": True},
            "export": {"related_key": "name", "label": "Enseigne"},
        },
    )
    project = relationship(
        "Project",
        primaryjoin="Task.project_id==Project.id",
        info={
            "colanderalchemy": {"exclude": True},
            "export": {"exclude": True},
        },
    )
    customer = relationship(
        "Customer",
        primaryjoin="Customer.id==Task.customer_id",
        backref=backref(
            "tasks",
            order_by="Task.date",
            info={
                "colanderalchemy": {"exclude": True},
                "export": {"exclude": True},
            },
        ),
        info={
            "colanderalchemy": {"exclude": True},
            "export": {"related_key": "label", "label": "Client"},
        },
    )
    business_type = relationship(
        "BusinessType", info={"colanderalchemy": {"exclude": True}}
    )
    business = relationship(
        "Business",
        primaryjoin="Business.id==Task.business_id",
        info={"colanderalchemy": {"exclude": True}},
    )

    # Content relationships
    discounts = relationship(
        "DiscountLine",
        info={
            "colanderalchemy": {"title": "Remises"},
            "export": {"exclude": True},
        },
        order_by="DiscountLine.tva",
        back_populates="task",
        cascade="all, delete-orphan",
    )
    # Lines that come after the TTC total for information purpose only
    # (eg: acomptes perçus non facturés, primes CEE, etc).
    # This does not modify amounts or calculations, and display a total due
    # for the customer.
    post_ttc_lines = relationship(
        "PostTTCLine",
        info={
            "colanderalchemy": {"title": "Remises post-TTC"},
            "export": {"exclude": True},
        },
        order_by="PostTTCLine.id",
        back_populates="task",
        cascade="all, delete-orphan",
    )
    payments = relationship(
        "BaseTaskPayment",
        primaryjoin="Task.id==BaseTaskPayment.task_id",
        info={
            "colanderalchemy": {"exclude": True},
            "export": {"exclude": True},
        },
        order_by="BaseTaskPayment.date",
        back_populates="task",
    )
    mentions = relationship(
        "TaskMention",
        secondary=TASK_MENTION,
        order_by="TaskMention.order",
        info={"export": {"exclude": True}},
    )
    mandatory_mentions = relationship(
        "TaskMention",
        secondary=MANDATORY_TASK_MENTION,
        order_by="TaskMention.order",
        info={"export": {"exclude": True}},
    )
    # Cet attribut a le même nom que le module CustomInvoiceBookEntry
    # configuré par le script de popuplate ce qui nous permet de faire
    # la jonction pour récupérer le taux d’assurance à appliquer
    insurance = relationship(
        "TaskInsuranceOption",
        info={"colanderalchemy": {"exclude": True}},
    )
    line_groups = relationship(
        "TaskLineGroup",
        order_by="TaskLineGroup.order",
        collection_class=ordering_list("order"),
        info={
            "colanderalchemy": {
                "title": "Unités d’œuvre",
                "validator": colander.Length(min=1, min_err="Une entrée est requise"),
                "missing": colander.required,
            },
            "export": {"exclude": True},
        },
        primaryjoin="TaskLineGroup.task_id==Task.id",
        back_populates="task",
        cascade="all, delete-orphan",
    )

    all_lines = relationship(
        "TaskLine",
        secondary="task_line_group",
        primaryjoin="Task.id==TaskLineGroup.task_id",
        secondaryjoin="TaskLineGroup.id==TaskLine.group_id",
        viewonly=True,
        back_populates="task",
        info={
            "colanderalchemy": {"exclude": True},
            "export": {"exclude": True},
        },
    )

    pdf_file = relationship(
        "File",
        primaryjoin="Task.pdf_file_id==File.id",
        cascade="all, delete",
        backref="associated_cached_task",
        info={"colanderalchemy": {"exclude": True}},
    )

    # Not used in latest invoices
    expenses = deferred(
        Column(
            BigInteger(),
            info={
                "export": {"exclude": True},
            },
            default=0,
        ),
        group="edit",
    )

    price_study = relationship(
        "PriceStudy",
        uselist=False,
        primaryjoin="PriceStudy.task_id==Task.id",
        back_populates="task",
        info={"colanderalchemy": {"exclude": True}},
        cascade="all, delete-orphan",
    )

    progress_invoicing_plan = relationship(
        "ProgressInvoicingPlan",
        uselist=False,
        primaryjoin="ProgressInvoicingPlan.task_id==Task.id",
        cascade="all, delete-orphan",
        back_populates="task",
        info={"colanderalchemy": {"exclude": True}},
    )
    # Configuré au niveau des Task pour inclure les CancelInvoice et les Invoices
    # (et les internal)
    exports = relationship(
        "InvoiceAccountingExportLogEntry",
        secondary=invoice_accounting_export_log_entry_association_table,
        back_populates="exported_invoices",
    )

    @property
    def _name_tmpl(self):
        if self.type_ == "task":
            # Does not happen in real life ; but might in pytests
            return "Task {0}"
        else:
            return f"{self.get_type_label()} {{0}}"

    _number_tmpl = "{s.company.name} {s.date:%Y-%m} F{s.company_index}"

    computer = None

    @classmethod
    def create(
        cls, request, customer, data: dict, no_price_study: bool = False
    ) -> "Task":
        return cls._caerp_service.create(request, customer, data, no_price_study)

    def __init__(self, user, company, project, **kw):
        company_index = self._get_company_index(company)
        project_index = self._get_project_index(project)

        self.status = "draft"
        self.company = company
        if "customer" in kw:
            customer = kw["customer"]
            self.address = customer.full_address
        self.owner = user
        self.status_user = user
        self.date = datetime.date.today()
        self.mode = project.mode
        if self.mode == "ttc":
            self.display_ttc = 1

        self.project = project

        # Initialize parts of the kw that may be required for label overrides
        for key, value in kw.items():
            if key not in ("date", "name"):
                setattr(self, key, value)

        self.set_numbers(company_index, project_index)

        # Initialize part of the kw that must come *after* set_numbers
        # set_numbers expect the current date, not the date arg.
        # This is arguable, but better keep historic behavior…
        if "date" in kw:
            self.date = kw["date"]

        # Allows name overriding, even if set_numbers() set one
        if "name" in kw:
            self.name = kw["name"]

        # We add a default task line group
        self.add_default_task_line_group()

    def duplicate(self, request, user, **kw):
        """
        DUplicate the current Task

        Mandatory args :

            user

                The user duplicating this Task

            customer

            project
        """
        return self._caerp_service.duplicate(request, self, user, **kw)

    def add_default_task_line_group(self):
        self.line_groups.append(TaskLineGroup(order=0))

    def _clean_task(self, request):
        """
        Delete all TaskLineGroups and Discounts attached to this Task
        """
        return self._caerp_service._clean_task(request, self)

    def frozen_settings_initialize(self):
        """
        Persist business specific labels on the Task object
        """
        overrides = self.naming_service.get_labels_for_business_type_id(
            self.business_type_id
        )
        return dict(label_overrides=overrides)

    def initialize_business_type_data(self):
        """
        Initialize the data related to the Task's business type

        - File requirements
        - Mandatory Mentions
        """
        self.file_requirement_service.populate(self)
        self.mention_service.populate(self)

    def update_indicators(self):
        """
        Update indicators related to this Task

        - Complete the indicators that are already satisfied
        """
        self.file_requirement_service.check_status(self)

    def get_file_requirements_status(self):
        """Return the status of the indicators concerning this Task"""
        return self.file_requirement_service.get_status(self)

    def get_file_requirements(self, scoped=False, file_type_id=None):
        """
        Return the file requirements related to this Task
        :param bool scoped: If True, return only the file requirements that are
        directly associated with this Task
        """
        if scoped:
            return self.file_requirement_service.get_attached_indicators(
                self, file_type_id
            )
        else:
            return self.file_requirement_service.get_related_indicators(
                self, file_type_id
            )

    def _get_project_index(self, project):
        """
        Return the index of the current object in the associated project
        :param obj project: A Project instance in which we will look to get the
        current doc index
        :returns: The next number
        :rtype: int
        """
        return -1

    def _get_company_index(self, company):
        """
        Return the index of the current object in the associated company
        :param obj company: A Company instance in which we will look to get the
        current doc index
        :returns: The next number
        :rtype: int
        """
        return -1

    def set_numbers(self, company_index, project_index):
        """
        Handle all attributes related to the given number

        :param int company_index: The index of the task in the company
        :param int project_index: The index of the task in its project
        """
        if company_index is None or project_index is None:
            raise Exception("Indexes should not be None")

        self.company_index = company_index
        self.project_index = project_index

        self.internal_number = self._number_tmpl.format(s=self)
        self.name = self._name_tmpl.format(project_index)

    def get_type_label(self):
        return self.naming_service.get_label_for_context(self.type_, self)

    @property
    def default_line_group(self):
        return self.line_groups[0]

    @property
    def attachments(self):
        """
        File that are attached to this task but not to any sale requirement
        """
        return self.file_requirement_service.get_other_attachments(self)

    def has_line_dates(self):
        for line in self.all_lines:
            if line.date:
                return True
        return False

    def max_lines_date(self):
        return max(i.date for i in self.all_lines if i is not None)

    def min_lines_date(self):
        return min(i.date for i in self.all_lines if i is not None)

    def fix_lines_mode(self):
        """
        Ensure that Task.mode is consistent with TaskLine.mode
        """
        for line in self.all_lines:
            if self.mode != line.mode:
                line.mode = self.mode
                DBSESSION().merge(line)

    def __json__(self, request) -> Dict[str, Any]:
        """
        Return the datas used by the json renderer to represent this task
        """
        result = dict(
            id=self.id,
            name=self.name,
            type_=self.type_,
            created_at=self.created_at,
            updated_at=self.updated_at,
            phase_id=self.phase_id,
            business_type_id=self.business_type_id,
            status=self.status,
            status_comment=self.status_comment,
            status_user_id=self.status_user_id,
            date=self.date,
            owner_id=self.owner_id,
            description=self.description,
            mode=self.mode,
            ht=integer_to_amount(self.ht, 5),
            tva=integer_to_amount(self.tva, 5),
            ttc=integer_to_amount(self.ttc, 5),
            company_id=self.company_id,
            project_id=self.project_id,
            customer_id=self.customer_id,
            project_index=self.project_index,
            company_index=self.company_index,
            official_number=self.official_number,
            internal_number=self.internal_number,
            display_units=self.display_units,
            display_ttc=self.display_ttc,
            expenses_ht=integer_to_amount(self.expenses_ht, 5),
            address=self.address,
            workplace=self.workplace,
            payment_conditions=self.payment_conditions,
            notes=self.notes,
            first_visit=self.first_visit,
            start_date=self.start_date,
            end_date=self.end_date,
            status_history=[
                status.__json__(request)
                for status in self.get_allowed_statuses(request)
            ],
            mentions=[mention.id for mention in self.mentions],
            insurance_id=self.insurance_id,
            input_mode=self._get_input_mode(),
            internal=self.internal,
        )
        if self.price_study:
            price_study_id = self.price_study.id
        else:
            price_study_id = None
        result["price_study_id"] = price_study_id
        return result

    @validates("status")
    def change_status(self, key, status):
        """
        fired on status change, barely logs what is happening
        """
        logger.debug("# Task status change #")
        current_status = self.status
        logger.debug(" + was {0}, becomes {1}".format(current_status, status))
        return status

    def get_company(self):
        """
        Return the company owning this task
        """
        return self.company

    def get_customer(self):
        """
        Return the customer of the current task
        """
        return self.customer

    def get_company_id(self):
        """
        Return the id of the company owning this task
        """
        return self.company.id

    def __repr__(self):
        return "<{s.type_} status:{s.status} id:{s.id}>".format(s=self)

    def get_groups(self):
        return [group for group in self.line_groups if group.lines]

    def get_tva_objects(self):
        return self._caerp_service.get_tva_objects(self)

    @classmethod
    def get_valid_invoices(cls, *args, **kwargs):
        return cls._caerp_service.get_valid_invoices(cls, *args, **kwargs)

    @classmethod
    def get_valid_estimations(cls, *args, **kwargs):
        return cls._caerp_service.get_valid_estimations(cls, *args, **kwargs)

    @classmethod
    def get_waiting_estimations(cls, *args):
        return cls._caerp_service.get_waiting_estimations(*args)

    @classmethod
    def get_waiting_invoices(cls, *args):
        return cls._caerp_service.get_waiting_invoices(cls, *args)

    @classmethod
    def query_by_validator_id(cls, validator_id: int, query=None):
        return cls._caerp_service.query_by_validator_id(cls, validator_id, query)

    @classmethod
    def query_by_antenne_id(cls, antenne_id: int, query=None, payment=False):
        return cls._caerp_service.query_by_antenne_id(cls, antenne_id, query, payment)

    @classmethod
    def query_by_follower_id(cls, follower_id: int, query=None, payment=False):
        return cls._caerp_service.query_by_follower_id(cls, follower_id, query, payment)

    @classmethod
    def total_income(cls, *args, **kwargs):
        return cls._caerp_service.total_income(cls, *args, **kwargs)

    @classmethod
    def total_estimated(cls, *args, **kwargs) -> int:
        return cls._caerp_service.total_estimated(cls, *args, **kwargs)

    def is_training(self):
        return self.business_type and self.business_type.name == "training"

    @classmethod
    def get_customer_task_factory(cls, customer):
        """
        Renvoie la classe à utiliser pour créer une Task pour le client donné
        """
        return cls._caerp_service.get_customer_task_factory(customer)

    @classmethod
    def find_task_status_date(cls, official_number, year):
        return cls._caerp_service.find_task_status_date(cls, official_number, year)

    def get_reference_number(self):
        """
        Retourne une référence au devis ou à la facture

        Si possible retourne uniquement l'index principal de la numérotation,
        sinon le numéro entier du document
        """
        from caerp.models.sequence_number import SequenceNumber

        sequence_number = (
            SequenceNumber.query()
            .filter(SequenceNumber.node_id == self.id)
            .order_by(desc(SequenceNumber.index))
            .first()
        )
        if sequence_number:
            return sequence_number.index
        elif self.official_number:
            return self.official_number
        else:
            return self.internal_number

    # Computing tools
    def _get_computer(self):
        """
        Return needed compute class depending on mode value
        :return: an instance of TaskCompute or TaskTtcCompute
        """
        if self.computer is None:
            if self.mode == "ttc":
                self.computer = TaskTtcCompute(self)
            else:
                self.computer = TaskCompute(self)
        return self.computer

    def floor(self, amount) -> int:
        return self._get_computer().floor(amount=amount)

    def total_ht(self) -> int:
        return self._get_computer().total_ht()

    def total_insurance(self, ht: int = None) -> int:
        return self.total_ht_rate("insurance", ht)

    def total_ttc(self):
        """
        TTC total without expenses (Same as total in newer Tasks)
        """
        return self._get_computer().total_ttc()

    def total(self):
        """
        Total TTC + expenses (Same as total_ttc in newer Tasks)
        """
        return self._get_computer().total()

    def expenses_amount(self):
        """
        Expense amounts (Not used in newer Tasks)
        """
        return self._get_computer().expenses_amount()

    def get_expense_ht(self):
        """
        Expense HT amount (Not used in newer Tasks)
        """
        return self._get_computer().get_expense_ht()

    def get_expenses_tva(self):
        """
        Expense TVA value (Not used in newer Tasks)
        """
        return self._get_computer().get_expenses_tva()

    def get_tvas(self) -> dict:
        """
        Build a dict grouping TVA amounts by tva values

        :returns: {tva_value: tva_amount} {2000: 2000000, 1000: 1000000}

        Tva value is in 10*2 format
        Tva amount is in 10*5 format
        """
        return self._get_computer().get_tvas()

    def has_multiple_tva(self) -> bool:
        """
        Returns True if there are several tvas in the document.
        """
        tva_not_null = []
        for amount in self.get_tvas().values():
            # Il est possible de mettre des lignes à 0 pour afficher des notes
            # On ne veut pas les compter
            if amount != 0:
                tva_not_null.append(amount)
        return len(tva_not_null) > 1

    def get_tvas_by_product(self):
        """
        Tva amounts grouped by products
        """
        return self._get_computer().get_tvas_by_product()

    def tva_amount(self):
        """
        Sum of TVA amounts
        """
        return self._get_computer().tva_amount()

    def tva_native_parts(self, with_discounts=True):
        """
        Build a dict grouping total HT or TTC (depending mode) amounts by associated tva
        """
        return self._get_computer().tva_native_parts(with_discounts)

    def tva_ht_parts(self, with_discounts=True):
        """
        Build a dict grouping total HT amounts by associated tva
        """
        return self._get_computer().tva_ht_parts(with_discounts)

    def tva_ttc_parts(self, with_discounts=True):
        """
        Build a dict gropuing total TTC amounts by associated TVA
        """
        return self._get_computer().tva_ttc_parts(with_discounts)

    def groups_total_ht(self):
        return self._get_computer().groups_total_ht()

    def groups_total_ttc(self):
        return self._get_computer().groups_total_ttc()

    def discount_total_ht(self):
        return self._get_computer().discount_total_ht()

    def add_ht_by_tva(self, ret_dict, lines):
        return self._get_computer().add_ht_by_tva(ret_dict=ret_dict, lines=lines)

    def post_ttc_total(self):
        return self._get_computer().post_ttc_total()

    def total_due(self):
        return self._get_computer().total_due()

    def json_totals(self, request):
        """
        Collect totals and returns a json representation of all values
        """
        return self._caerp_service.json_totals(request, self)

    def format_amount(self, amount, trim=True, grouping=True, precision=2):
        return self._caerp_service.format_amount(
            self, amount, trim, grouping, precision
        )

    def set_auto_validated(self):
        """Set Task as auto_validated"""
        self.auto_validated = True

    def get_rate(self, rate_name: str) -> float:
        return self._caerp_service.get_rate(self, rate_name)

    def get_rate_level(self, rate_name: str) -> str:
        return self._caerp_service.get_rate_level(self, rate_name)

    def total_ht_rate(self, rate_name: str, ht: int = None) -> int:
        """
        Compute the amount that will be covered by the "rate_name" contribution

        :param str rate_name: contribution/insurance ...
        """
        return self._get_computer().total_ht_rate(rate_name, ht)

    def set_display_units(self):
        """
        Set last display_units value used by the company
        :return: number
        """
        default = Config.get_value("task_display_units_default")
        query = DBSESSION().query(Task.display_units)
        query = query.filter(Task.company_id == self.company_id)
        query = query.filter(Task.id != self.id)
        query = query.order_by(desc(Task.id)).limit(1)
        last_display_units = query.scalar()
        if last_display_units in (0, 1):
            default = last_display_units
        self.display_units = default

    def set_display_ttc(self):
        """
        Set last display_ttc value used by the company
        :return: number
        """
        default = Config.get_value("task_display_ttc_default")
        query = DBSESSION().query(Task.display_ttc)
        query = query.filter(Task.company_id == self.company_id)
        query = query.filter(Task.id != self.id)
        query = query.order_by(desc(Task.id)).limit(1)
        last_display_ttc = query.scalar()
        if last_display_ttc in (0, 1):
            default = last_display_ttc
        self.display_ttc = default

    def set_price_study(self, request):
        return self._caerp_service.set_price_study(request, self)

    def get_price_study(self):
        return self.price_study

    def has_price_study(self):
        return self.price_study is not None

    def unset_price_study(self, request):
        return self._caerp_service.unset_price_study(request, self)

    def set_progress_invoicing_plan(self, request):
        return self._caerp_service.set_progress_invoicing_plan(request, self)

    def get_progress_invoicing_plan(self):
        return self.progress_invoicing_plan

    def has_progress_invoicing_plan(self):
        return self.progress_invoicing_plan is not None

    def unset_progress_invoicing_plan(self, request):
        return self._caerp_service.unset_progress_invoicing_plan(request, self)

    def _get_input_mode(self):
        """
        The way TaskLines are configured

        in case we use a price_study, we've got intermediate models used to generate
        TaskLineGroups and TaskLines
        """
        if self.has_price_study():
            return "price_study"
        else:
            return "classic"

    def cache_totals(self, request=None):
        """
        Cache Task totals from outside events scope

        :param obj request: The Pyramid request
        """
        self._caerp_service.cache_totals(request, self)

    def get_selectable_tvas(self):
        if self.internal:
            internal = Tva.get_internal()
            if internal is not None:
                result = [internal]
            else:
                result = []
        else:
            result = Tva.get_external()
        return result

    def get_selectable_products(self):
        if self.internal:
            result = Product.get_internal()
        else:
            result = Product.get_external()
        return result

    def get_default_tva(self, tva_options=None):
        """
        Return the default tva to be used in this specific context

        - The last used in the document
        or
        - The default one

        :param obj request: The pyramid request with a Task context
        :param list tva_options: The available options for the end user
        :rtype: str
        """
        result = None

        # On récupère la liste des TVA possibles si elle n'est pas fournie
        if tva_options is None:
            tva_options = self.get_selectable_tvas()

        # On utilise la dernière TVA du doc si elle fait partie des TVA possibles
        tva_value = None
        if len(self.all_lines) > 0:
            tva_value = self.all_lines[-1].tva
        if tva_value is not None:
            for tva in tva_options:
                if tva.value == tva_value:
                    result = tva
                    break

        # Si on a pas encore de TVA, on prend celle par configurée par défaut
        # ou la première possible faute de mieux pour les documents internes
        if result is None:
            if self.internal:
                if tva_options:
                    result = tva_options[0]
                for tva_opt in tva_options:
                    if tva_opt.default:
                        result = tva_opt
                        break
            else:
                result = Tva.get_default()

        return result

    def get_default_product_id(self, products=None, default_tva=None):
        """
        Try to find a default product_id regarding the current context

        :param obj request: A pyramid request with a Task context
        :param list products: A list of Product instances
        :param obj tva: The default tva

        :rtype: int or None
        """
        if default_tva is None:
            default_tva = self.get_default_tva()
        if products is None:
            products = self.get_selectable_products()

        result = None

        if len(products) == 1:
            result = products[0].id
        elif default_tva and len(default_tva.products) == 1:
            result = default_tva.products[0].id
        return result

    def on_before_commit(self, request, action, changes=None):
        """
        Handles actions to be run before commiting modifications to the current Task
        """
        return self._caerp_service.on_before_commit(request, self, action, changes)

    def get_short_internal_number(self):
        """
        Return task's internal number without the company name
        """
        return self.internal_number.replace(self.company.name, "").strip()


class DiscountLine(DBBASE):
    """
    A discount line
    """

    __tablename__ = "discount"
    __table_args__ = default_table_args
    id = Column(
        Integer,
        primary_key=True,
        nullable=False,
    )
    task_id = Column(
        Integer,
        ForeignKey(
            "task.id",
            ondelete="cascade",
        ),
        info={
            "colanderalchemy": {
                "title": "Identifiant du document",
            }
        },
    )
    description = Column(Text)
    amount = Column(BigInteger(), info={"colanderalchemy": {"title": "Montant"}})
    tva = Column(Integer, nullable=False, default=0)
    task = relationship(
        "Task",
        uselist=False,
        info={"colanderalchemy": {"exclude": True}},
        back_populates="discounts",
    )

    _caerp_service = DiscountLineService

    def __json__(self, request):
        return dict(
            id=self.id,
            task_id=self.task_id,
            description=self.description,
            amount=integer_to_amount(self.amount, 5),
            tva=integer_to_amount(self.tva, 2),
            mode=self.task.mode,
        )

    def duplicate(self):
        """
        return the equivalent InvoiceLine
        """
        line = DiscountLine()
        line.tva = self.tva
        line.amount = self.amount
        line.description = self.description
        return line

    @classmethod
    def from_price_study_discount(cls, discount):
        return cls._caerp_service.from_price_study_discount(discount)

    def __repr__(self):
        return "<DiscountLine amount : {s.amount} tva:{s.tva} id:{s.id}>".format(s=self)

    def _get_computer(self):
        """
        Return needed compute class depending on mode value
        :return: an instance of DiscountLineCompute or DiscountLineTtcCompute
        """
        if self.task and self.task.mode == "ttc":
            return DiscountLineTtcCompute(self)
        else:
            return DiscountLineCompute(self)

    def total_ht(self):
        return self._get_computer().total_ht()

    def tva_amount(self):
        return self._get_computer().tva_amount()

    def total(self):
        return self._get_computer().total()

    def get_tva(self):
        return self._get_computer().get_tva()

    def on_before_commit(self, request, state, attributes=None):
        """
        Handle actions before commit

        :param obj request: Pyramid request
        :param str state: A str (add/update/delete)
        :param dict attributes: The attributes that were recently modified
        (default None)
        """
        return self._caerp_service.on_before_commit(request, self, state, attributes)

    def get_company_id(self):
        return self.task.company_id


class TaskLineGroup(DBBASE):
    """
    Group of lines
    """

    __table_args__ = default_table_args
    id = Column(Integer, primary_key=True)
    task_id = Column(
        Integer,
        ForeignKey("task.id", ondelete="cascade"),
        info={
            "colanderalchemy": {
                "title": "Identifiant du document",
            }
        },
    )
    description = Column(Text(), default="")
    title = Column(String(255), default="")
    order = Column(Integer, default=1)

    # Doit-on afficher le détail des prestations dans le document final ?
    display_details = Column(Boolean(), default=True)

    task = relationship(
        "Task",
        primaryjoin="TaskLineGroup.task_id==Task.id",
        info={"colanderalchemy": {"exclude": True}},
        back_populates="line_groups",
    )
    lines = relationship(
        "TaskLine",
        order_by="TaskLine.order",
        back_populates="group",
        collection_class=ordering_list("order"),
        info={
            "colanderalchemy": {
                "title": "Prestations",
            }
        },
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    price_study_chapter = relationship(
        "PriceStudyChapter",
        uselist=False,
        back_populates="task_line_group",
        info={"colanderalchemy": {"exclude": True}},
    )
    progress_invoicing_chapter = relationship(
        "ProgressInvoicingChapter",
        uselist=False,
        back_populates="task_line_group",
        info={"colanderalchemy": {"exclude": True}},
    )
    _caerp_service = TaskLineGroupService

    def __json__(self, request):
        return dict(
            id=self.id,
            title=self.title,
            description=self.description,
            task_id=self.task_id,
            order=self.order,
            lines=[line.__json__(request) for line in self.lines],
            mode=self.task.mode,
            display_details=self.display_details,
            total_ht=integer_to_amount(self.total_ht(), 5),
            total_ttc=integer_to_amount(self.total_ttc(), 5),
        )

    def duplicate(self):
        return self._caerp_service.duplicate(self)

    def gen_cancelinvoice_group(self, request):
        return self._caerp_service.gen_cancelinvoice_group(request, self)

    @classmethod
    def from_price_study_product(cls, product):
        """
        Build an instance based on the given BasePriceStudyProduct
        """
        return cls._caerp_service.from_price_study_product(cls, product)

    @classmethod
    def from_sale_product_work(cls, product, document=None, quantity=1):
        """
        Build an instance based on the given SaleProductWork

        :param obj product: The original SaleProductWork
        :param obj document: The Estimatin/Invoice ...
        """
        return cls._caerp_service.from_sale_product_work(
            cls,
            product,
            document=document,
            quantity=quantity,
        )

    def _get_computer(self):
        """
        Return needed compute class depending on mode value
        :return: an instance of GroupCompute or GroupTtcCompute
        """
        if self.task.mode == "ttc":
            return GroupTtcCompute(self)
        else:
            return GroupCompute(self)

    def total_ttc(self):
        return self._get_computer().total_ttc()

    def get_tvas(self):
        return self._get_computer().get_tvas()

    def get_tvas_by_product(self):
        return self._get_computer().get_tvas_by_product()

    def tva_amount(self):
        return self._get_computer().tva_amount()

    def total_ht(self):
        return self._get_computer().total_ht()

    def __repr__(self):
        return "<TaskLineGroup id:{s.id} task_id:{s.task_id}".format(s=self)

    def on_before_commit(self, request, state, attributes=None):
        """
        Handle actions before commit

        :param obj request: Pyramid request
        :param str state: A str (add/update/delete)
        :param dict attributes: The attributes that were recently modified
        (default None)
        """
        return self._caerp_service.on_before_commit(request, self, state, attributes)

    def get_company_id(self):
        return self.task.company_id


class TaskLine(DBBASE):
    """
    Estimation/Invoice/CancelInvoice lines
    """

    __table_args__ = default_table_args
    id = Column(
        Integer,
        primary_key=True,
        info={"colanderalchemy": {"widget": deform.widget.HiddenWidget()}},
    )
    group_id = Column(
        Integer,
        ForeignKey("task_line_group.id", ondelete="cascade"),
        info={"colanderalchemy": {"exclude": True}},
    )
    order = Column(
        Integer,
        default=1,
    )
    description = Column(Text)
    # ttc or ht compute base
    mode = Column(
        String(10),
        info={
            "colanderalchemy": {"title": "Mode de saisie"},
            "export": {"exclude": True},
        },
        default="ht",
    )
    # .cost can contain unit HT or unit TTC, depending on .mode
    cost = Column(
        BigInteger(),
        info={
            "colanderalchemy": {
                "title": "Montant",
            }
        },
        default=0,
    )
    date = Column(
        Date(),
        info={"colanderalchemy": {"title": "Date d’exécution"}},
        nullable=True,
    )

    @hybrid_property
    def year(self):
        if self.date:
            return self.date.year
        else:
            return None

    @year.expression
    def year(cls):
        return extract("year", cls.date)

    @hybrid_property
    def month(self):
        if self.date:
            return self.date.month
        else:
            return None

    @month.expression
    def month(cls):
        return extract("month", cls.date)

    quantity = Column(
        Float(), info={"colanderalchemy": {"title": "Quantité"}}, default=1
    )
    unity = Column(
        String(100),
        info={"colanderalchemy": {"title": "Unité"}},
    )
    tva = Column(
        Integer,
        info={"colanderalchemy": {"title": "Tva (en %)"}},
        nullable=False,
        default=2000,
    )
    product_id = Column(
        Integer,
        ForeignKey("product.id", ondelete="SET NULL"),
    )
    group = relationship(
        TaskLineGroup,
        primaryjoin="TaskLine.group_id==TaskLineGroup.id",
        info={"colanderalchemy": {"exclude": True}},
        back_populates="lines",
    )
    product = relationship(
        "Product",
        primaryjoin="Product.id==TaskLine.product_id",
        uselist=False,
        foreign_keys=product_id,
        info={"colanderalchemy": {"exclude": True}},
    )

    task = relationship(
        "Task",
        uselist=False,
        secondary="task_line_group",
        primaryjoin="TaskLine.group_id==TaskLineGroup.id",
        secondaryjoin="TaskLineGroup.task_id==Task.id",
        viewonly=True,
        back_populates="all_lines",
        info={
            "colanderalchemy": {"exclude": True},
            "export": {"exclude": True},
        },
    )
    price_study_product = relationship(
        "BasePriceStudyProduct",
        uselist=False,
        back_populates="task_line",
        info={"colanderalchemy": {"exclude": True}},
    )
    progress_invoicing_product = relationship(
        "ProgressInvoicingBaseProduct",
        uselist=False,
        back_populates="task_line",
        info={"colanderalchemy": {"exclude": True}},
    )
    _caerp_service = TaskLineService
    computer = None

    def duplicate(self):
        """
        duplicate a line
        """
        return self._caerp_service.duplicate(self)

    def gen_cancelinvoice_line(self):
        """
        Return a cancel invoice line duplicating this one
        """
        return self._caerp_service.gen_cancelinvoice_line(self)

    def __repr__(self):
        return (
            "<TaskLine id:{s.id} task_id:{s.group.task_id} cost:{s.cost} "
            " quantity:{s.quantity} tva:{s.tva} product_id:{s.product_id}>".format(
                s=self
            )
        )

    def __json__(self, request):
        result = dict(
            id=self.id,
            order=self.order,
            mode=self.mode,
            cost=integer_to_amount(self.cost, 5),
            tva=integer_to_amount(self.tva, 2),
            description=self.description,
            quantity=self.quantity,
            unity=self.unity,
            group_id=self.group_id,
            product_id=self.product_id,
            date=self.date.isoformat() if self.date else None,
        )
        return result

    @hybrid_property
    def is_in_hours(self):
        return is_hours(self.unity)

    @is_in_hours.expression
    def is_in_hours(self):
        return self.unity.ilike("heure%") | func.lower(self.unity).in_(HOUR_UNITS)

    @classmethod
    def from_sale_product(cls, sale_product, document=None, quantity=1):
        """
        Build an instance based on the given sale_product

        :param obj sale_product: A SaleProduct instance
        :pararm obj document: The Estimation/Invoice...
        :returns: A TaskLine instance
        """
        return cls._caerp_service.from_sale_product(
            cls, sale_product, document, quantity
        )

    @classmethod
    def from_price_study_product(cls, product):
        return cls._caerp_service.from_price_study_product(cls, product)

    @classmethod
    def from_price_study_work(cls, work):
        return cls._caerp_service.from_price_study_work(cls, work)

    @classmethod
    def from_price_study_work_item(cls, work_item):
        return cls._caerp_service.from_price_study_work_item(cls, work_item)

    @classmethod
    def from_sale_product_work_item(cls, work_item, document=None, quantity=1):
        """
        Build an instance based on the given SaleProductWorkItem
        """
        return cls._caerp_service.from_sale_product_work_item(
            cls, work_item, document, quantity
        )

    def _get_computer(self):
        """
        Return needed compute class depending on mode value
        :return: an instance of LineCompute or LineTtcCompute
        """
        if self.computer is None:
            if self.mode == "ttc":
                self.computer = LineTtcCompute(self)
            else:
                self.computer = LineCompute(self)
        return self.computer

    def get_tva(self):
        return self._get_computer().get_tva()

    def unit_ht(self):
        return self._get_computer().unit_ht()

    def unit_ttc(self):
        return self._get_computer().unit_ttc()

    def total_ht(self):
        return self._get_computer().total_ht()

    def tva_amount(self):
        return self._get_computer().tva_amount()

    def total(self):
        return self._get_computer().total()

    def on_before_commit(self, request, state, attributes=None):
        """
        Handle actions before commit

        :param obj request: Pyramid request
        :param str state: A str (add/update/delete)
        :param dict attributes: The attributes that were recently modified
        (default None)
        """
        return self._caerp_service.on_before_commit(request, self, state, attributes)

    def get_company_id(self):
        return self.task.company_id


class PostTTCLine(DBBASE):
    """
    A content line that come after the TTC total for information purpose only
    (eg: acomptes perçus non facturés, primes CEE)
    """

    __tablename__ = "post_ttc_line"
    __table_args__ = default_table_args
    id = Column(
        Integer,
        primary_key=True,
        nullable=False,
    )
    task_id = Column(Integer, ForeignKey("task.id", ondelete="cascade"))
    label = Column(String(100), info={"colanderalchemy": {"title": "Libellé"}})
    amount = Column(BigInteger(), info={"colanderalchemy": {"title": "Montant"}})
    task = relationship(
        "Task",
        uselist=False,
        info={"colanderalchemy": {"exclude": True}},
        back_populates="post_ttc_lines",
    )

    _caerp_service = PostTTCLineService

    def __json__(self, request):
        return dict(
            id=self.id,
            task_id=self.task_id,
            label=self.label,
            amount=integer_to_amount(self.amount, 5),
        )

    def __repr__(self):
        return "<PostTTCLine label:{s.label} amount : {s.amount} id:{s.id}>".format(
            s=self
        )

    def on_before_commit(self, request, state, attributes=None):
        """
        Handle actions before commit

        :param obj request: Pyramid request
        :param str state: A str (add/update/delete)
        :param dict attributes: The attributes that were recently modified
        (default None)
        """
        return self._caerp_service.on_before_commit(request, self, state, attributes)

    def get_company_id(self):
        return self.task.get_company_id()


def cache_amounts(mapper, connection, target):
    """
    Set amounts in the cached amount vars to be able to provide advanced search
    ... options in the invoice list page
    """
    logger.info("Caching the task amounts")
    if target is not None:
        target.ht = target.total_ht()
        target.tva = target.tva_amount()
        target.ttc = target.total()


def cache_parent_amounts(mapper, connection, target):
    """
    Set amounts in the cached amount vars to be able to provide advanced search
    ... options in the invoice list page
    """
    # Buggy since the original modification is not yet persisted
    # Ref https://framagit.org/caerp/caerp/issues/1055
    if hasattr(target, "task"):
        logger.info("Caching the parent task amounts")
        task = target.task
        if task is not None:
            task.ht = task.total_ht()
            task.tva = task.tva_amount()
            task.ttc = task.total()


def freeze_settings(mapper, connection, target):
    if not target.frozen_settings:
        # Freezing is only done once
        target.freeze_settings()

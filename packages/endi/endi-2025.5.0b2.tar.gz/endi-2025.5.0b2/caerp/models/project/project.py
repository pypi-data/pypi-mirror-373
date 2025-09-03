"""
    Project model
"""
import datetime

from sqlalchemy import (
    Table,
    Column,
    Integer,
    String,
    ForeignKey,
    Text,
    Boolean,
    Date,
    UniqueConstraint,
)
from sqlalchemy.orm import (
    deferred,
    relationship,
)

from caerp_base.models.base import (
    default_table_args,
    DBBASE,
)
from caerp.models.node import Node
from .services.project import ProjectService
from caerp.models.services.sale_file_requirements import (
    ProjectFileRequirementService,
)
from .mixins import BusinessMetricsMixin


ProjectCustomer = Table(
    "project_customer",
    DBBASE.metadata,
    Column("project_id", Integer, ForeignKey("project.id")),
    Column("customer_id", Integer, ForeignKey("customer.id")),
    UniqueConstraint("project_id", "customer_id", name="uniq_idx"),
    mysql_charset=default_table_args["mysql_charset"],
    mysql_engine=default_table_args["mysql_engine"],
)

ProjectBusinessType = Table(
    "project_business_type",
    DBBASE.metadata,
    Column("project_id", Integer, ForeignKey("project.id")),
    Column("business_type_id", Integer, ForeignKey("business_type.id")),
    mysql_charset=default_table_args["mysql_charset"],
    mysql_engine=default_table_args["mysql_engine"],
)


class Project(BusinessMetricsMixin, Node):
    """
    The project model
    """

    __tablename__ = "project"
    __table_args__ = default_table_args
    __mapper_args__ = {"polymorphic_identity": "project"}
    fk_filter_field = "project_id"  # BusinessMetricsMixin

    id = Column(
        ForeignKey("node.id"),
        primary_key=True,
        info={"colanderalchemy": {"exclude": True}},
    )

    code = Column(
        String(12),
        info={
            "colanderalchemy": {"title": "Code", "description": "Max 12 caractères."}
        },
    )

    description = deferred(
        Column(
            String(150),
            info={
                "colanderalchemy": {
                    "title": "Description succinte",
                    "description": "Max 150 caractères",
                }
            },
        ),
        group="edit",
    )

    company_id = Column(
        Integer,
        ForeignKey("company.id"),
        info={
            "options": {"csv_exclude": True},
            "colanderalchemy": {"exclude": True},
        },
    )

    starting_date = deferred(
        Column(
            Date(),
            info={
                "colanderalchemy": {
                    "title": "Date de début",
                }
            },
            default=datetime.date.today,
        ),
        group="edit",
    )

    ending_date = deferred(
        Column(
            Date(),
            info={
                "colanderalchemy": {
                    "title": "Date de fin",
                }
            },
            default=datetime.date.today,
        ),
        group="edit",
    )

    definition = deferred(
        Column(
            Text,
            info={"label": "Définition", "colanderalchemy": {"title": "Définition"}},
        ),
        group="edit",
    )

    archived = Column(
        Boolean(),
        default=False,
        info={"colanderalchemy": {"exclude": True}},
    )

    project_type_id = Column(
        ForeignKey("project_type.id"),
        info={
            "label": "Type de projet",
            "colanderalchemy": {"title": "Type de projet"},
        },
    )

    mode = Column(
        String(10),
        info={
            "colanderalchemy": {"title": "Mode de saisie"},
            "export": {"exclude": True},
        },
        default="ht",
    )

    customers = relationship(
        "Customer",
        secondary=ProjectCustomer,
        back_populates="projects",
        info={
            "colanderalchemy": {
                "title": "Client",
                "exclude": True,
            },
            "export": {"exclude": True},
        },
    )
    business_types = relationship(
        "BusinessType",
        secondary=ProjectBusinessType,
        info={
            "colanderalchemy": {
                "title": "Types de sous-dossier proposés en plus du type par défaut",
            }
        },
    )
    phases = relationship(
        "Phase",
        back_populates="project",
        cascade="all, delete-orphan",
        info={"colanderalchemy": {"exclude": True}, "export": {"exclude": True}},
    )

    businesses = relationship(
        "Business",
        primaryjoin="Project.id==Business.project_id",
        back_populates="project",
        cascade="all, delete-orphan",
        info={"colanderalchemy": {"exclude": True}, "export": {"exclude": True}},
    )
    tasks = relationship(
        "Task",
        primaryjoin="Task.project_id==Project.id",
        back_populates="project",
        order_by="Task.date",
        info={
            "colanderalchemy": {"exclude": True},
            "export": {"exclude": True},
        },
    )
    estimations = relationship(
        "Estimation",
        primaryjoin="Estimation.project_id==Project.id",
        order_by="Estimation.date",
        info={
            "colanderalchemy": {"exclude": True},
            "export": {"exclude": True},
        },
    )
    invoices = relationship(
        "Invoice",
        primaryjoin="Invoice.project_id==Project.id",
        order_by="Invoice.date",
        info={
            "colanderalchemy": {"exclude": True},
            "export": {"exclude": True},
        },
    )
    cancelinvoices = relationship(
        "CancelInvoice",
        primaryjoin="CancelInvoice.project_id==Project.id",
        order_by="Invoice.date",
        info={
            "colanderalchemy": {"exclude": True},
            "export": {"exclude": True},
        },
    )
    project_type = relationship("ProjectType")
    company = relationship(
        "Company",
        primaryjoin="Project.company_id==Company.id",
        info={
            "colanderalchemy": {"exclude": True},
            "export": {"exclude": True, "py3o": {"exclude": False}},
        },
    )

    _caerp_service = ProjectService
    file_requirement_service = ProjectFileRequirementService

    def get_all_business_types(self, request):
        """
        Return all the business types that can used in the given project
        """
        business_types = []
        if self.project_type.default_business_type:
            business_types.append(self.project_type.default_business_type)

        for business_type in self.business_types:
            # Dans certains cas le type par défaut est aussi dans les "autres"
            # types (Cas du changement de type de dossier)
            if business_type != self.project_type.default_business_type:
                if business_type.allowed(request):
                    business_types.append(business_type)
        return business_types

    def __json__(self, request):
        """
        Return a dict view of this object
        """
        phases = [phase.__json__(request) for phase in self.phases]

        return dict(
            id=self.id,
            name=self.name,
            code=self.code,
            definition=self.definition,
            description=self.description,
            archived=self.archived,
            mode=self.mode,
            phases=phases,
            business_types=self.get_all_business_types(request),
        )

    def has_tasks(self):
        return self._caerp_service.count_tasks(self) > 0

    def is_deletable(self):
        """
        Return True if this project could be deleted
        """
        return self.archived and not self.has_tasks()

    def get_company_id(self):
        return self.company_id

    def get_next_estimation_index(self):
        return self._caerp_service.get_next_estimation_index(self)

    def get_next_invoice_index(self):
        return self._caerp_service.get_next_invoice_index(self)

    def get_next_cancelinvoice_index(self):
        return self._caerp_service.get_next_cancelinvoice_index(self)

    def get_used_business_type_ids(self):
        return self._caerp_service.get_used_business_type_ids(self)

    def has_internal_customer(self):
        return self._caerp_service.has_internal_customer(self)

    @classmethod
    def check_phase_id(cls, project_id, phase_id):
        return cls._caerp_service.check_phase_id(project_id, phase_id)

    @classmethod
    def label_query(cls):
        return cls._caerp_service.label_query(cls)

    @classmethod
    def get_code_list_with_labels(cls, company_id):
        return cls._caerp_service.get_code_list_with_labels(cls, company_id)

    @classmethod
    def get_customer_projects(cls, customer_id):
        return cls._caerp_service.get_customer_projects(cls, customer_id)

    @classmethod
    def query_for_select(cls, company_id):
        """
        Build a sqla query suitable for a select widget

        :param int company_id: The company the projects are attached to
        """
        return cls._caerp_service.query_for_select(cls, company_id)

    def get_file_requirements(self, scoped=False, file_type_id=None):
        """Return the project file requirements"""
        return self.file_requirement_service.get_attached_indicators(self, file_type_id)

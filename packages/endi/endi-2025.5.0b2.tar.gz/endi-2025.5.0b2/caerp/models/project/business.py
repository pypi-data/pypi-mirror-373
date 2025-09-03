from caerp_base.models.base import DBBASE, DBSESSION, default_table_args
from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    Date,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from caerp.models.node import Node
from caerp.models.services.sale_file_requirements import BusinessFileRequirementService

from .mixins import BusinessMetricsMixin
from .services.business import BusinessService
from .services.business_status import BusinessStatusService


class BusinessPaymentDeadline(DBBASE):
    __tablename__ = "business_payment_deadline"
    __table_args__ = default_table_args
    id = Column(Integer, primary_key=True)
    deposit = Column(Boolean(), default=False)
    order = Column(Integer, info={"colanderalchemy": {"title": "Ordre"}}, default=1)
    description = Column(
        Text,
        info={"colanderalchemy": {"title": "Description"}},
    )
    amount_ttc = Column(
        BigInteger(),
        info={"colanderalchemy": {"title": "Montant TTC"}},
    )
    amount_ht = Column(
        BigInteger(),
        info={"colanderalchemy": {"title": "Montant HT"}},
    )
    date = Column(
        Date(), info={"colanderalchemy": {"title": "Date"}}, nullable=True, default=None
    )
    business_id = Column(Integer, ForeignKey("business.id", ondelete="CASCADE"))
    estimation_payment_id = Column(
        Integer, ForeignKey("estimation_payment.id", ondelete="CASCADE")
    )
    estimation_id = Column(Integer, ForeignKey("estimation.id", ondelete="CASCADE"))
    # Invoice is valid ?
    invoiced = Column(Boolean(), default=False)
    # Associated invoice
    invoice_id = Column(Integer, ForeignKey("invoice.id", ondelete="SET NULL"))
    payment_line = relationship("PaymentLine")
    estimation = relationship("Estimation")
    invoice = relationship("Invoice")
    business = relationship("Business", back_populates="payment_deadlines")

    def __str__(self):
        return "<BusinessPaymentDeadline id:{}>".format(self.id)

    def resulted(self):
        """
        Return True if this deadline has been invoiced and the invoice
        has been resulted
        """
        return self.invoiced and self.invoice.is_resulted()

    def invoicing(self):
        """
        Return True if this deadline has been invoiced and the invoice has
        not been validated yet
        """
        return self.invoice_id is not None and not self.invoiced


class Business(BusinessMetricsMixin, Node):
    """
    Permet de :

        * Collecter les fichiers

        * Regrouper devis/factures/avoirs

        * Calculer le CA d'une affaire

        * Générer les factures

        * Récupérer le HT à dépenser

        * Des choses plus complexes en fonction du type de business

    Business.estimations
    Business.invoices
    Business.invoices[0].cancelinvoices
    """

    __tablename__ = "business"
    __table_args__ = default_table_args
    __mapper_args__ = {"polymorphic_identity": "business"}
    file_requirement_service = BusinessFileRequirementService
    status_service = BusinessStatusService
    _caerp_service = BusinessService
    fk_filter_field = "business_id"  # BusinessMetricsMixin

    id = Column(
        Integer,
        ForeignKey("node.id"),
        primary_key=True,
        info={"colanderalchemy": {"exclude": True}},
    )
    status = Column(
        String(8),
        default="danger",
        info={"colanderalchemy": {"title": "Statut de cette affaire"}},
    )

    business_type_id = Column(
        ForeignKey("business_type.id"),
        info={"colanderalchemy": {"title": "Type d'affaires"}},
    )
    project_id = Column(
        ForeignKey("project.id"),
        info={"colanderalchemy": {"exclude": True}},
        nullable=False,
    )

    # Le mode de facturation de l'affaire classic / progress
    invoicing_mode = Column(String(20), default="classic")
    PROGRESS_MODE = "progress"
    CLASSIC_MODE = "classic"

    # L'affaire doit-elle être visible ou non
    visible = Column(
        Boolean(), default=False, info={"colanderalchemy": {"exclude": True}}
    )
    # Relations
    business_type = relationship(
        "BusinessType",
    )
    project = relationship(
        "Project",
        primaryjoin="Project.id == Business.project_id",
    )
    tasks = relationship(
        "Task", primaryjoin="Task.business_id==Business.id", back_populates="business"
    )
    estimations = relationship(
        "Task",
        back_populates="business",
        primaryjoin=(
            "and_(Task.business_id==Business.id, "
            "Task.type_.in_(('estimation', 'internalestimation')))"
        ),
    )
    invoices = relationship(
        "Task",
        back_populates="business",
        primaryjoin=(
            "and_(Task.business_id==Business.id, "
            "Task.type_.in_(('invoice', 'cancelinvoice', 'internalinvoice', "
            "'internalcancelinvoice')))"
        ),
        order_by="Task.date,Task.id",
    )
    invoices_only = relationship(
        "Invoice",
        primaryjoin="Task.business_id==Business.id",
        info={
            "colanderalchemy": {"exclude": True},
            "export": {"exclude": True},
        },
    )

    payment_deadlines = relationship(
        "BusinessPaymentDeadline",
        primaryjoin="BusinessPaymentDeadline.business_id==Business.id",
        order_by="BusinessPaymentDeadline.order",
        cascade="all, delete-orphan",
    )
    indicators = relationship(
        "CustomBusinessIndicator",
        primaryjoin="CustomBusinessIndicator.business_id==Business.id",
        cascade="all, delete-orphan",
    )
    # Statut de Ce qui doit être facture
    progress_invoicing_chapter_statuses = relationship(
        "ProgressInvoicingChapterStatus",
        back_populates="business",
        cascade="all, delete-orphan",
    )
    # Ce qui est facturé
    progress_invoicing_plans = relationship(
        "ProgressInvoicingPlan", back_populates="business", cascade="all, delete-orphan"
    )

    supplier_invoice_lines = relationship(
        "SupplierInvoiceLine",
        back_populates="business",
    )
    base_expense_lines = relationship(
        "BaseExpenseLine",
        back_populates="business",
    )

    @classmethod
    def create(cls, name, project, business_type) -> "Business":
        visible = project.project_type.with_business or business_type.bpf_related
        result = cls(
            name=name,
            project=project,
            business_type_id=business_type.id,
            visible=visible,
        )
        DBSESSION().add(result)
        DBSESSION().flush()
        return result

    @property
    def payment_lines(self):
        """
        Collect payment lines that are referenced by a deadline
        """
        return [
            deadline.payment_line
            for deadline in self.payment_deadlines
            if deadline.payment_line is not None
        ]

    @property
    def invoiced(self):
        indicator = self.status_service.get_or_create_invoice_indicator(self)
        return indicator.status == indicator.SUCCESS_STATUS

    def get_company_id(self):
        return self.project.company_id

    def get_customer(self):
        return self._caerp_service.get_customer(self)

    def amount_to_invoice(self, column_name="ht"):
        """
        Compute the amount to invoice in this business
        :param: column_name : ht/ttc
        :returns: The amount in the *10^5 precision
        :rtype: int
        """
        return self._caerp_service.to_invoice(self, column_name)

    def populate_indicators(self) -> "Business":
        """
        Populate Business related indicators

        To be run after creation

        :returns: The business we manage
        """
        self.status_service.populate_indicators(self)
        return self

    def populate_file_requirements(self):
        self.file_requirement_service.populate(self)
        self.file_requirement_service.check_status(self)
        return self

    def get_file_requirements(self, scoped=False, file_type_id=None):
        """
        Return the file requirements related to this business
        :param bool scoped: If True, return only the file requirements that are
        directly associated with this business
        """
        if scoped:
            return self.file_requirement_service.get_attached_indicators(
                self, file_type_id
            )
        else:
            return self.file_requirement_service.get_related_indicators(
                self, file_type_id
            )

    def get_file_requirements_status(self):
        """Return the status of the indicators concerning this Task"""
        return self.file_requirement_service.get_status(self)

    def populate_deadlines(self, estimation=None):
        """
        Populate the current business with its associated payment deadlines
        regarding the estimations belonging to this business

        :param obj estimation: An optionnal Estimation instance
        :returns: This instance
        """
        return self._caerp_service.populate_deadlines(self, estimation)

    def find_deadline(self, deadline_id):
        """
        Find the deadline matching this id

        :param int deadline_id: The deadline id
        :returns: A Payment instance
        """
        return self._caerp_service.find_deadline(self, deadline_id)

    def find_deadline_from_invoice(self, invoice):
        """
        Find the deadline associated to the current business and the given
        invoice

        :param obj invoice: The Invoice we're working on
        :returns: A BusinessPaymentDeadline instance
        """
        return self._caerp_service.find_deadline_from_invoice(self, invoice)

    def get_next_deadline(self, request) -> BusinessPaymentDeadline:
        """
        Return the next deadline for the current business

        :param obj request: The current request
        :param obj business: The current business
        :returns: A BusinessPaymentDeadline instance
        """
        return self._caerp_service.get_next_deadline(request, self)

    def add_estimation(self, request, user):
        """
        Generate a new estimation attached to the current business

        :param obj user: The user generating the estimation
        :rtype: class caerp.models.task.estimation.Estimation
        """
        return self._caerp_service.add_estimation(request, self, user)

    def add_invoice(self, request, user):
        """
        Generate a new invoice attached to the current business

        :param obj user: The user generating the invoice
        :rtype: class caerp.models.task.invoice.Invoice
        """
        return self._caerp_service.add_invoice(request, self, user)

    def is_void(self):
        """
        Check if the current business is Void
        :rtype: bool
        """
        return self._caerp_service.is_void(self)

    def invoicing_years(self):
        """
        List the financial years of related invoices
        :rtype: list
        """
        return self._caerp_service.invoicing_years(self)

    # Progress Invoicing related methods
    def set_progress_invoicing_mode(self, request):
        """
        Change invoicing_mode to progress and populate
        """
        self.invoicing_mode = self.PROGRESS_MODE
        self._caerp_service.populate_progress_invoicing_status(request, self)

    def unset_progress_invoicing_mode(self, request):
        """
        Change invoicing_mode to classic and clear progress_invoicing related
        elements
        """
        self.invoicing_mode = self.CLASSIC_MODE
        self._caerp_service.clear_progress_invoicing_status(request, self)

    def populate_progress_invoicing_status(
        self, request, exclude_estimation=None, invoice=None
    ):
        """
        Populate the progress invoicing statuses

        :param obj exclude_estimation: Estimation to be excluded from treatment
        """
        self._caerp_service.populate_progress_invoicing_status(
            request, self, exclude_estimation, invoice
        )

    def populate_progress_invoicing_cancelinvoice(
        self, request, invoice, cancelinvoice
    ):
        """
        Populate the Progress Invoicing Plan associated to a cancelinvoice
        :param obj plan: ProgressInvoicingPlan
        """
        return self._caerp_service.populate_progress_invoicing_cancelinvoice(
            request, self, invoice, cancelinvoice
        )

    def add_progress_invoicing_invoice(self, request, user):
        """
        Generate a new invoice attached to the current business

        :param obj user: The user generating the invoice
        :rtype: class caerp.models.task.invoice.Invoice
        """
        return self._caerp_service.add_progress_invoicing_invoice(request, self, user)

    def add_progress_invoicing_sold_invoice(self, request, user):
        """
        Generate the last invoice
        """
        return self._caerp_service.add_progress_invoicing_sold_invoice(
            request, self, user
        )

    def on_task_delete(self, request, task):
        """
        Callback launched when a draft task has been deleted in the business

        :param obj task: The deleted Task
        """
        self._caerp_service.on_task_delete(request, self, task)

    def on_estimation_signed_status_change(self, request):
        """
        Callback launched when estimation signed_status changes
        """
        self._caerp_service.on_estimation_signed_status_change(request, self)

    def has_previous_invoice(self, invoice):
        """
        Test if the business has a previous invoice (chronologically)

        :param Invoice invoice: The Invoice object
        :rtype: bool
        """
        return self._caerp_service.has_previous_invoice(self, invoice)

    def get_current_invoice(self):
        """
        Test if the business has an invoice that is currently edited

        :rtype: Invoice/CancelInvoice
        """
        return self._caerp_service.get_current_invoice(self)

    def progress_invoicing_is_complete(self):
        """
        Check if this business has been invoiced totally

        :returns: True if it's completely invoiced
        :rtype: bool
        """
        return self._caerp_service.progress_invoicing_is_complete(self)

    def __json__(self, request):
        return {"id": self.id, "name": self.name}

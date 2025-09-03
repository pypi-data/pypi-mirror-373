import datetime
import logging
from typing import Union

from beaker.cache import cache_region
from caerp_base.models.base import DBBASE, DBSESSION, default_table_args
from caerp_base.models.mixins import OfficialNumberMixin
from sqlalchemy import (
    Boolean,
    Column,
    Date,
    Enum,
    ForeignKey,
    Integer,
    String,
    Table,
    distinct,
)
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import backref, relationship
from sqlalchemy.sql.functions import func

from caerp.compute.expense import (
    ExpenseCompute,
    ExpenseKmLineCompute,
    ExpenseLineCompute,
)
from caerp.compute.math_utils import integer_to_amount
from caerp.models.export.accounting_export_log import (
    expense_accounting_export_log_entry_association_table,
)
from caerp.models.node import Node
from caerp.models.project.mixins import BusinessLinkedModelMixin
from caerp.models.status import PaidStatusHolderMixin, ValidationStatusHolderMixin
from caerp.utils import strings
from caerp.utils.datetimes import format_date

from .services import BaseExpenseLineService
from .services.sheet import ExpenseSheetService

logger = logging.getLogger(__name__)


class ExpenseSheet(
    OfficialNumberMixin,
    ValidationStatusHolderMixin,
    ExpenseCompute,
    PaidStatusHolderMixin,
    Node,
):
    """
    Model representing a whole ExpenseSheet
    An expensesheet is related to a company and an employee (one user may
    have multiple expense sheets if it has multiple companies)
    :param company_id: The user's company id
    :param user_id: The user's id
    :param year: The year the expense is related to
    :param month: The month the expense is related to
    :param status: Status of the sheet
    :param status_user: The user related to statuschange
    :param lines: expense lines of this sheet
    """

    __tablename__ = "expense_sheet"
    __table_args__ = default_table_args
    __mapper_args__ = {"polymorphic_identity": "expensesheet"}
    validation_date_column = "date"

    _caerp_service = ExpenseSheetService

    id = Column(
        ForeignKey("node.id"),
        primary_key=True,
        info={"colanderalchemy": {"exclude": True}},
    )
    month = Column(
        Integer,
        info={
            "colanderalchemy": {
                "title": "Mois",
            }
        },
    )
    year = Column(
        Integer,
        info={
            "colanderalchemy": {
                "title": "Année",
            }
        },
    )
    title = Column(
        String(255),
        info={
            "colanderalchemy": {
                "title": "Titre",
            }
        },
    )
    justified = Column(
        Boolean(),
        default=False,
        info={
            "colanderalchemy": {
                "title": "Justificatifs reçus et acceptés",
            }
        },
    )
    purchase_exported = Column(
        Boolean(),
        default=False,
        info={
            "colanderalchemy": {"title": "Les achats ont déjà été exportés ?"},
        },
    )
    expense_exported = Column(
        Boolean(),
        default=False,
        info={
            "colanderalchemy": {"title": "Les frais ont déjà été exportés ?"},
        },
    )
    company_id = Column(
        Integer,
        ForeignKey("company.id", ondelete="cascade"),
        info={"colanderalchemy": {"exclude": True}},
    )
    user_id = Column(
        Integer,
        ForeignKey("accounts.id"),
        info={"colanderalchemy": {"exclude": True}},
    )

    # Relationships
    lines = relationship(
        "ExpenseLine",
        back_populates="sheet",
        order_by="ExpenseLine.date",
        info={"colanderalchemy": {"title": "Dépenses"}},
        cascade="all, delete-orphan",
        passive_deletes=True,
        overlaps="kmlines,sheet",
    )
    kmlines = relationship(
        "ExpenseKmLine",
        back_populates="sheet",
        order_by="ExpenseKmLine.date",
        info={"colanderalchemy": {"title": "Dépenses kilométriques"}},
        cascade="all, delete-orphan",
        passive_deletes=True,
        overlaps="lines,sheet",
    )
    company = relationship(
        "Company",
        primaryjoin="ExpenseSheet.company_id==Company.id",
    )
    user = relationship(
        "User",
        primaryjoin="ExpenseSheet.user_id==User.id",
        info={
            "colanderalchemy": {"exclude": True},
        },
        backref=backref(
            "expenses",
            order_by="ExpenseSheet.month",
            info={
                "colanderalchemy": {"exclude": True},
                "export": {"exclude": True},
            },
            cascade="all, delete-orphan",
        ),
    )
    payments = relationship(
        "ExpensePayment",
        order_by="ExpensePayment.date",
        cascade="all, delete-orphan",
        info={"colanderalchemy": {"exclude": True}},
    )
    exports = relationship(
        "ExpenseAccountingExportLogEntry",
        secondary=expense_accounting_export_log_entry_association_table,
        back_populates="exported_expenses",
    )
    sepa_waiting_payments = relationship(
        "ExpenseSepaWaitingPayment",
        primaryjoin="ExpenseSheet.id==foreign(ExpenseSepaWaitingPayment.node_id)",
        back_populates="expense_sheet",
        info={"colanderalchemy": {"exclude": True}},
        passive_deletes=True,
    )

    def __json__(self, request):
        return dict(
            id=self.id,
            name=self.name,
            created_at=self.created_at.isoformat(),
            updated_at=self.updated_at.isoformat(),
            company_id=self.company_id,
            user_id=self.user_id,
            paid_status=self.paid_status,
            justified=self.justified,
            status=self.status,
            status_user_id=self.status_user_id,
            status_date=self.status_date.date().isoformat(),
            status_history=[
                status.__json__(request)
                for status in self.get_allowed_statuses(request)
            ],
            lines=[line.__json__(request) for line in self.lines],
            kmlines=[line.__json__(request) for line in self.kmlines],
            month=self.month,
            month_label=strings.month_name(self.month),
            year=self.year,
            title=self.title,
            attachments=[
                f.__json__(request) for f in self.children if f.type_ == "file"
            ],
        )

    @hybrid_property
    def date(self):
        """
        Date property used to match the official_numbering system

        See : https://framagit.org/caerp/caerp/-/issues/2596
        """
        return datetime.date(self.year, self.month, 1)

    @date.expression
    def date(cls):
        return func.date(func.concat(cls.year, "-", cls.month, "-", 1))

    def get_company_id(self):
        """
        Return the if of the company associated to this model
        """
        return self.company_id

    def duplicate(self, year, month):
        sheet = ExpenseSheet()
        sheet.month = month
        sheet.year = year
        sheet.user_id = self.user_id
        sheet.company_id = self.company_id
        for line in self.lines:
            line.duplicate(sheet)

        for line in self.kmlines:
            line.duplicate(sheet)

        return sheet

    @property
    def global_status(self):
        """
        Compile a global status essentially used to match css rules

        :rtype: str
        """
        if self.paid_status == "paid":
            result = "partial_caution"
        else:
            result = self.status
        return result

    def get_lines_justified_status(self) -> Union[None, bool]:
        return self._caerp_service.get_lines_justified_status(self)

    @property
    def files(self):
        """
        Return all files related to the expense sheet
        """
        return [f for f in self.children if f.type_ == "file"]

    def has_waiting_payment(self) -> bool:
        return self.get_waiting_payment() is not None

    def get_waiting_payment(self):
        for payment in self.sepa_waiting_payments:
            if payment.paid_status == payment.WAIT_STATUS:
                return payment


class BaseExpenseLine(DBBASE, BusinessLinkedModelMixin):
    """
    Base models for expense lines
    :param type: Column for polymorphic discrimination
    :param date: Date of the expense
    :param description: description of the expense
    :param code: analytic code related to this expense
    :param valid: validation status of the expense
    :param sheet_id: id of the expense sheet this expense is related to
    """

    __tablename__ = "baseexpense_line"
    __table_args__ = default_table_args
    __mapper_args__ = dict(
        polymorphic_on="type",
        polymorphic_identity="line",
        with_polymorphic="*",
    )
    _caerp_service = BaseExpenseLineService
    parent_model = ExpenseSheet

    id = Column(
        Integer,
        primary_key=True,
        info={"colanderalchemy": {"exclude": True}},
    )
    type = Column(
        String(30),
        nullable=False,
        info={"colanderalchemy": {"exclude": True}},
    )
    date = Column(
        Date(),
        default=datetime.date.today,
        info={"colanderalchemy": {"title": "Date"}},
    )
    description = Column(
        String(255),
        info={"colanderalchemy": {"title": "Description"}},
        default="",
    )
    category = Column(Enum("1", "2", name="category"), default="1")
    valid = Column(
        Boolean(),
        default=True,
        info={"colanderalchemy": {"title": "Valide ?"}},
    )
    type_id = Column(
        Integer,
        info={
            "colanderalchemy": {
                "title": "Type de dépense",
            }
        },
    )
    sheet_id = Column(
        Integer,
        ForeignKey("expense_sheet.id", ondelete="cascade"),
        info={"colanderalchemy": {"exclude": True}},
    )

    expense_type = relationship(
        "ExpenseType",
        primaryjoin="BaseExpenseLine.type_id==ExpenseType.id",
        uselist=False,
        foreign_keys=type_id,
        info={"colanderalchemy": {"exclude": True}},
    )

    sheet = relationship(
        "ExpenseSheet",
        primaryjoin="BaseExpenseLine.sheet_id==ExpenseSheet.id",
        uselist=False,
        foreign_keys=sheet_id,
        info={"colanderalchemy": {"exclude": True}},
    )

    def long_label(self):
        expense_line_long_label = "{} {}€ ({}) − {}".format(
            self.description,
            strings.format_amount(self.total, grouping=False),
            self.expense_type.label,
            format_date(self.date),
        )
        if self.sheet.title:
            expense_line_long_label += " {}".format(self.sheet.title)
        return expense_line_long_label

    @classmethod
    def linkable(cls, business):
        return cls._caerp_service.linkable(cls, business)

    @classmethod
    def query_linked_to(cls, target: "BusinessMetricsMixin"):
        return cls._caerp_service.query_linked_to(cls, target)

    @classmethod
    def total_expense(
        cls,
        query_filters=[],
        column_name="total_ht",
        tva_on_margin: bool = None,
    ) -> int:
        return cls._caerp_service.total_expense(
            cls, query_filters, column_name, tva_on_margin
        )

    def get_company_id(self):
        """Used in the permission management"""
        return self.sheet.company_id

    def __json__(self, request):
        ret = dict(
            id=self.id,
            date=self.date,
            description=self.description,
            category=self.category,
            valid=self.valid,
            type_id=self.type_id,
            sheet_id=self.sheet_id,
            customer_id=self.customer_id,
            project_id=self.project_id,
            business_id=self.business_id,
        )
        ret.update(
            dict(
                BusinessLinkedModelMixin.__json__(self, request),
            )
        )
        return ret

    def duplicate(self, sheet):
        result = self.__class__(sheet=sheet)
        for key in (
            "category",
            "description",
            "customer_id",
            "business_id",
            "project_id",
            "ht",
        ):
            value = getattr(self, key)
            setattr(result, key, value)

        # Fix #3473
        if sheet == self.sheet:
            result.date = self.date
        else:
            result.date = sheet.date
        return result


EXPENSE_LINE_FILE = Table(
    "expense_line_file",
    DBBASE.metadata,
    Column(
        "expense_line_id",
        Integer,
        ForeignKey("expense_line.id", ondelete="cascade"),
        nullable=False,
    ),
    Column(
        "file_id", Integer, ForeignKey("file.id", ondelete="cascade"), nullable=False
    ),
    mysql_charset=default_table_args["mysql_charset"],
    mysql_engine=default_table_args["mysql_engine"],
)


class ExpenseLine(BaseExpenseLine, ExpenseLineCompute):
    """
    Common Expense line
    """

    __tablename__ = "expense_line"
    __table_args__ = default_table_args
    __mapper_args__ = dict(polymorphic_identity="expenseline")

    id = Column(
        Integer,
        ForeignKey("baseexpense_line.id", ondelete="cascade"),
        primary_key=True,
        info={"colanderalchemy": {"exclude": True}},
    )
    ht = Column(
        Integer,
        info={
            "colanderalchemy": {
                "title": "Montant HT",
            }
        },
    )
    tva = Column(
        Integer,
        info={
            "colanderalchemy": {
                "title": "Montant de la TVA",
            }
        },
    )
    manual_ttc = Column(
        Integer,
        info={
            "colanderalchemy": {
                "title": "Montant TTC saisi",
            }
        },
        default=0,
    )
    supplier_id = Column(
        Integer,
        ForeignKey("supplier.id"),
        info={
            "export": {"exclude": True},
        },
    )
    invoice_number = Column(
        String(255),
        default="",
        nullable=False,
    )
    justified = Column(
        Boolean(),
        default=False,
        nullable=False,
        info={
            "colanderalchemy": {
                "title": "Justificatifs reçus et acceptés",
            }
        },
    )
    # Relationships
    supplier = relationship(
        "Supplier",
        primaryjoin="Supplier.id==ExpenseLine.supplier_id",
        info={
            "colanderalchemy": {"exclude": True},
            "export": {"exclude": True},
        },
    )
    sheet = relationship(
        "ExpenseSheet",
        info={"colanderalchemy": {"exclude": True}},
        back_populates="lines",
    )
    files = relationship(
        "File",
        secondary=EXPENSE_LINE_FILE,
        info={"export": {"exclude": True}},
    )

    def __json__(self, request):
        res = BaseExpenseLine.__json__(self, request)
        res.update(
            dict(
                ht=integer_to_amount(self.ht, 2, 0),
                tva=integer_to_amount(self.tva, 2, 0),
                manual_ttc=integer_to_amount(self.manual_ttc, 2, 0),
                files=[f.id for f in self.files],
                supplier_id=self.supplier_id,
                invoice_number=self.invoice_number,
                justified=self.justified,
            )
        )
        return res

    def duplicate(self, sheet=None):
        line = super().duplicate(sheet)
        line.type_id = self.type_id
        line.tva = self.tva
        line.manual_ttc = self.manual_ttc
        line.supplier_id = self.supplier_id
        line.invoice_number = self.invoice_number
        return line


class ExpenseKmLine(BaseExpenseLine, ExpenseKmLineCompute):
    """
    Model representing a specific expense related to kilometric fees
    :param start: starting point
    :param end: endpoint
    :param km: Number of kilometers
    :param ht: HT amount
    """

    __tablename__ = "expensekm_line"
    __table_args__ = default_table_args
    __mapper_args__ = dict(polymorphic_identity="expensekmline")
    id = Column(
        Integer,
        ForeignKey("baseexpense_line.id", ondelete="cascade"),
        primary_key=True,
        info={"colanderalchemy": {"exclude": True}},
    )
    start = Column(
        String(150),
        default="",
        info={"colanderalchemy": {"title": "Point de départ"}},
    )
    end = Column(
        String(150),
        default="",
        info={"colanderalchemy": {"title": "Point d'arrivée"}},
    )
    km = Column(
        Integer,
        info={
            "colanderalchemy": {
                "title": "Nombre de kilomètres",
            }
        },
    )
    ht = Column(
        Integer,
        info={"colanderalchemy": {"exclude": True}},
    )
    sheet = relationship(
        "ExpenseSheet",
        uselist=False,
        info={"colanderalchemy": {"exclude": True}},
        back_populates="kmlines",
    )

    def __json__(self, request):
        res = BaseExpenseLine.__json__(self, request)
        res.update(
            dict(
                km=integer_to_amount(self.km),
                ht=integer_to_amount(self.ht, 2, 0),
                start=self.start,
                end=self.end,
                vehicle=self.vehicle,
            )
        )
        return res

    @property
    def vehicle(self):
        return self.expense_type.label

    def on_before_commit(self, request, state, attributes=None):
        sync = False
        if state == "add":
            sync = True
        elif state == "update":
            if not attributes:
                sync = True
            else:
                for key in "km", "expense_type_id":
                    if key in attributes:
                        sync = True
                        break
        if sync:
            self.cache_ht(request)

    def cache_ht(self, request):
        self.ht = self.km * self.expense_type.amount
        request.dbsession.merge(self)

    def duplicate(self, sheet):
        expense_type = self.expense_type.get_by_year(sheet.year)
        line = None
        if expense_type is not None:
            line = super().duplicate(sheet)
            line.expense_type = expense_type
            line.start = self.start
            line.end = self.end
            line.km = self.km
        return line


def get_expense_years(kw):
    """
    Return the list of years that there were some expense configured
    """

    @cache_region("long_term", "expenseyears")
    def expenseyears():
        """
        return distinct expense years available in the database
        """
        query = DBSESSION().query(distinct(ExpenseSheet.year))
        query = query.order_by(ExpenseSheet.year)
        years = [year[0] for year in query]
        current = datetime.date.today().year
        if current not in years:
            years.append(current)
        return years

    return expenseyears()


def get_new_expense_years(kw):
    current = datetime.date.today().year
    return [
        current - 1,
        current,
        current + 1,
        current + 2,
    ]


def get_expense_sheet_name(month, year):
    """
    Return the name of an expensesheet
    """
    return "expense_{0}_{1}".format(month, year)

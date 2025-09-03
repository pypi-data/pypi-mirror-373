from caerp_base.models import DBSESSION
from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
)
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship


class BusinessMetricsMixin:
    """
    Group methods to compute « business intelligence » metrics/agregates.

    Require from implementors :
      - a self._caerp_service with the methods :
        - get_total_income()
        - get_total_estimated()

      - a fk_filter_field property, a column name that must be present on
        BusinessLinkedModelMixin implementors
    """

    def get_total_expenses(self, tva_on_margin: bool = None, mode="ht"):
        """
        Total linked expenses, cumulating Expense Sheet lines and Supplier Invoice lines

        :param tva_on_margin:
           if None, counts all linked expenses
           if True, only linked expenses that are in tva_on_margin mode
           if False, only linked expenses that are *not* in tva_on_margin mode
        :returns: decimal encoded as integer, precision=2
        """
        from caerp.models.supply import SupplierInvoiceLine
        from caerp.models.expense.sheet import BaseExpenseLine

        if tva_on_margin is not None or mode == "ttc":
            column_name = "total"  # ttc
        else:
            column_name = "total_ht"

        return sum(
            Class.total_expense(
                [getattr(Class, self.__class__.fk_filter_field) == self.id],
                tva_on_margin=tva_on_margin,
                column_name=column_name,
            )
            for Class in (BaseExpenseLine, SupplierInvoiceLine)
        )

    def get_total_income(self, column_name="ht") -> int:
        """
        :returns: decimal encoded as integer, precision=5
        """
        return self._caerp_service.get_total_income(self, column_name=column_name)

    def get_total_estimated(self, column_name="ht") -> int:
        """
        :returns: decimal encoded as integer, precision=5
        """
        return self._caerp_service.get_total_estimated(self, column_name)

    def has_nonvalid_expenses(self) -> bool:
        """
        :returns true if get_total_estimated() use expense/supplier invoice lines with status≠valid
        """
        from caerp.models.supply import SupplierInvoiceLine
        from caerp.models.expense.sheet import BaseExpenseLine

        for Class in (BaseExpenseLine, SupplierInvoiceLine):
            query = Class.query_linked_to(self)
            query = query.filter(Class.parent_model.status != "valid")
            if DBSESSION.query(query.exists()).scalar():
                return True

        return False

    def get_total_margin(self, tva_on_margin: bool = None) -> int:
        """
        :param tva_on_margin:
           if None, counts all linked expenses
           if True, only linked expenses that are in tva_on_margin mode
        :returns: decimal encoded as integer, precision=5
        """
        # expenses are encoded with 2 decimals, incomes with 5 decimals
        if tva_on_margin:
            column_name = "ttc"
        else:
            column_name = "ht"
        expenses = self.get_total_expenses(tva_on_margin=tva_on_margin) * 1000
        income = self.get_total_income(column_name=column_name)
        return income - expenses

    def get_topay(self) -> int:
        # Note : les business.invoices incluent les avoirs (d'où le hasattr)
        return sum(
            [invoice.topay() for invoice in self.invoices if hasattr(invoice, "topay")]
        )


class BusinessLinkedModelMixin:
    """
    Champs pour les modèles qui sont liés optionellement à un client ou dossier
    ou affaire (ou inclusif !).

    La logique doit être respectée (ex: l'affaire doit appartenir au bon client).
    """

    @property
    @classmethod
    def parent_model(cls):
        """
        the model class that contains our model
        """
        raise NotImplementedError

    @declared_attr
    def customer_id(cls):
        return Column(
            Integer,
            ForeignKey("customer.id", ondelete="SET NULL"),
            nullable=True,
            info={"colanderalchemy": {"title": "Client concerné"}},
        )

    @declared_attr
    def project_id(cls):
        return Column(
            Integer,
            ForeignKey("project.id", ondelete="SET NULL"),
            nullable=True,
            info={"colanderalchemy": {"title": "Dossier concerné"}},
        )

    @declared_attr
    def business_id(cls):
        return Column(
            Integer,
            ForeignKey("business.id", ondelete="SET NULL"),
            nullable=True,
            info={"colanderalchemy": {"title": "Affaire concernée"}},
        )

    @declared_attr
    def customer(cls):
        return relationship("Customer", info={"colanderalchemy": {"exclude": True}})

    @declared_attr
    def project(cls):
        return relationship("Project", info={"colanderalchemy": {"exclude": True}})

    @declared_attr
    def business(cls):
        return relationship("Business", info={"colanderalchemy": {"exclude": True}})

    def link_to(self, target):
        """
        Links instance to a Business-related target object

        And update other business-related fields consistently.

        :param target: instance of Customer, Business or Project
        """
        from caerp.models.project.business import Business
        from caerp.models.project import Project
        from caerp.models.third_party.customer import Customer

        if not isinstance(target, (Business, Project, Customer)):
            raise ValueError("Cannot link to {}".format(target))
        else:
            self.business_id = None
            self.project_id = None

        if isinstance(target, Customer):
            self.customer_id = target.id
        elif isinstance(target, Project):
            self.project_id = target.id
            if len(target.customers) == 1:
                self.customer_id = target.customers[0].id

        elif isinstance(target, Business):
            self.business_id = target.id
            self.project_id = target.project_id
            self.customer_id = target.get_customer().id

    def __json__(self, request):
        ret = {}
        customer_label, business_label, project_label = "", "", ""

        if self.customer is not None:
            customer_label = self.customer.name
        if self.project is not None:
            project_label = self.project.name
        if self.business is not None:
            business_label = self.business.name

        ret.update(
            dict(
                customer_id=self.customer_id,
                business_id=self.business_id,
                project_id=self.project_id,
                customer_label=customer_label,
                project_label=project_label,
                business_label=business_label,
            )
        )
        return ret

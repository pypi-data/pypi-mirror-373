import logging

from dataclasses import dataclass, field
from typing import List, Optional
from sqlalchemy import or_
from sqlalchemy.orm import with_polymorphic, load_only


from caerp.models.node import Node
from caerp.models.project.project import ProjectCustomer, Project
from caerp.models.project import Business

from caerp.utils.controller import BaseAddEditController, RelatedAttrManager
from caerp.models.task import Task, Estimation, Invoice, CancelInvoice

logger = logging.getLogger(__name__)


class ProjectRelatedAttrManager(RelatedAttrManager):
    def _add_related_customer_ids(self, project: Project, project_dict: dict) -> dict:
        result = self.dbsession.query(ProjectCustomer.c.customer_id).filter(
            ProjectCustomer.c.project_id == project.id
        )
        project_dict["customer_ids"] = [p[0] for p in result]
        return project_dict

    def _add_related_phases(self, project: Project, project_dict: dict) -> dict:
        project_dict["phases"] = [
            phase.__json__(self.request) for phase in project.phases
        ]
        return project_dict

    def _add_related_business_types(self, project: Project, project_dict: dict) -> dict:
        project_dict["business_types"] = [
            btype.__json__(self.request)
            for btype in project.get_all_business_types(self.request)
        ]
        if project.project_type.default_business_type:
            project_dict[
                "default_business_type_id"
            ] = project.project_type.default_business_type.id
        return project_dict


class ProjectAddEditController(BaseAddEditController):
    related_manager_factory = ProjectRelatedAttrManager

    def after_add_edit(self, project: Project, edit: bool, attributes: dict) -> Project:
        """
        Post formatting Hook

        :param project: Current project (added/edited)

        :param edit: Is it an edit form ?

        :param attributes: Validated attributes sent to this view

        :return: The modified project
        """
        if not edit:
            project.company = self.context

        return project


class NullClass:
    """Class to be used as a placeholder for None"""

    pass


@dataclass
class CustomerData:
    id: int
    label: str

    def __json__(self, request):
        return {"id": self.id, "label": self.label}


@dataclass
class InvoiceData:
    id: int
    type_: str
    name: str
    status: str
    business_type_id: str
    business_id: int
    official_number: str
    customer: Optional[CustomerData] = None

    @classmethod
    def from_model(cls, model):
        return cls(
            id=model.id,
            type_=model.type_,
            name=model.name,
            status=model.status,
            business_id=model.business_id,
            business_type_id=model.business_type_id,
            official_number=model.official_number,
        )

    def __json__(self, request):
        result = {
            "id": self.id,
            "type_": self.type_,
            "name": self.name,
            "status": self.status,
            "business_type_id": self.business_type_id,
            "business_id": self.business_id,
            "official_number": self.official_number,
        }
        if self.customer is not None:
            result["customer"] = self.customer.__json__(request)
        return result


@dataclass
class EstimationData:
    id: int
    type_: str
    name: str
    status: str
    business_type_id: str
    internal_number: str
    business_id: Optional[int] = None
    customer: Optional[CustomerData] = None

    @classmethod
    def from_model(cls, model):
        return cls(
            id=model.id,
            type_=model.type_,
            name=model.name,
            status=model.status,
            internal_number=model.internal_number,
            business_id=model.business_id,
            business_type_id=model.business_type_id,
        )

    def __json__(self, request):
        result = {
            "id": self.id,
            "type_": self.type_,
            "name": self.name,
            "status": self.status,
            "internal_number": self.internal_number,
            "business_type_id": self.business_type_id,
            "business_id": self.business_id,
        }
        if self.customer is not None:
            result["customer"] = self.customer.__json__(request)
        return result


@dataclass
class BusinessData:
    id: int
    type_: str
    name: str
    status: str
    estimations: List[EstimationData] = field(default_factory=list)
    invoices: List[InvoiceData] = field(default_factory=list)

    @classmethod
    def from_model(cls, model):
        return cls(
            id=model.id,
            type_=model.type_,
            name=model.name,
            status=model.status,
        )

    def __json__(self, request):
        result: dict = {
            "id": self.id,
            "type_": self.type_,
            "name": self.name,
            "status": self.status,
        }
        result["estimations"] = [item.__json__(request) for item in self.estimations]
        result["invoices"] = [item.__json__(request) for item in self.invoices]
        return result


@dataclass
class ProjectData:
    id: int
    type_: str
    name: str
    estimations: List[EstimationData] = field(default_factory=list)
    invoices: List[InvoiceData] = field(default_factory=list)
    businesses: List[BusinessData] = field(default_factory=list)

    @classmethod
    def from_model(cls, model):
        return cls(
            id=model.id,
            type_=model.type_,
            name=model.name,
        )

    def __json__(self, request):
        result: dict = {"id": self.id, "type_": self.type_, "name": self.name}
        result["estimations"] = [item.__json__(request) for item in self.estimations]
        result["invoices"] = [item.__json__(request) for item in self.invoices]
        result["businesses"] = [item.__json__(request) for item in self.businesses]
        return result


class ProjectTreeController:
    """
    Controller getting the project tree with businesses and tasks

    {
        'id':
        'name':
        'estimations': [{'id': '....'}]
        'businesses': [
            {'id': '....', 'estimations': [{}..], 'invoices:'[{}...]}
        ]
    }
    """

    node_polymorphic_alias = with_polymorphic(Node, [Business, Project, Task])
    invoice_columns = [
        Task.id,
        Task.name,
        Task.official_number,
        Task.status,
        Task.business_id,
        Task.business_type_id,
    ]
    estimation_columns = [
        Estimation.id,
        Estimation.type_,
        Estimation.name,
        Estimation.status,
        Estimation.business_id,
        Estimation.business_type_id,
        Estimation.internal_number,
    ]
    business_columns = [
        Business.id,
        Business.type_,
        Business.name,
        Business.status,
    ]

    def __init__(self, request, project):
        self.request = request
        self.project = project
        if len(self.project.customers) > 1:
            self.multi_customers = True
        else:
            self.multi_customers = False

    def _collect_estimations(
        self, business_id: Optional[int] = None, task_id: Optional[int] = None
    ) -> List[EstimationData]:
        """Collect Estimation models filtered with project_id and business_id"""
        query = (
            self.request.dbsession.query(Estimation)
            .options(load_only(*self.estimation_columns))
            .filter(Estimation.project_id == self.project.id)
        )
        if task_id is not None:
            query = query.filter(Estimation.id == task_id)

        # Est appelé depuis collect_businesses
        if business_id is not None:
            query = query.filter(Estimation.business_id == business_id)
        # Est appelé depuis collect_project
        else:
            query = query.outerjoin(Estimation.business).filter(
                or_(Estimation.business_id == None, Business.visible == False)
            )

        query = query.order_by(Estimation.date.desc(), Estimation.status)
        return [EstimationData.from_model(estimation) for estimation in query]

    def _collect_invoices(
        self, business_id: Optional[int] = None, task_id: Optional[int] = None
    ) -> List[InvoiceData]:
        """Collect Invoices filtered on project and business id"""
        query = (
            self.request.dbsession.query(Task)
            .with_polymorphic([Invoice, CancelInvoice])
            .filter(Task.type_.in_(Task.invoice_types))
            .options(load_only(*self.invoice_columns))
            .filter(Task.project_id == self.project.id)
        )

        if task_id is not None:
            query = query.filter(Task.id == task_id)
        if business_id is not None:
            query = query.filter(Task.business_id == business_id)
        else:
            query = query.join(Invoice.business).filter(Business.visible == False)

        query = query.order_by(Task.date.desc(), Task.status)
        return [InvoiceData.from_model(invoice) for invoice in query]

    def _collect_businesses(
        self, business_id: Optional[int] = None, task_id: Optional[int] = None
    ) -> List[BusinessData]:
        if not business_id:
            query = (
                self.request.dbsession.query(Business)
                .options(load_only(*self.business_columns))
                .filter(Business.project_id == self.project.id)
                .order_by(Business.updated_at.desc(), Business.status)
            )
        else:
            query = self.request.dbsession.query(Business).filter(
                Business.id == business_id
            )
        result = []
        for business in query:
            data = BusinessData.from_model(business)
            data.estimations = self._collect_estimations(business.id, task_id)
            data.invoices = self._collect_invoices(business.id, task_id)
            result.append(data)
        return result

    def _collect_project(
        self, business_id: Optional[int] = None, task_id: Optional[int] = None
    ) -> ProjectData:
        """
        Collect the element ids for which we want the associated files

        Order node ids

            - projects
            - estimations without business
            - business
                - associated estimations
                - associated invoices
        """
        project = ProjectData.from_model(self.project)
        # on collecte les devis et factures sans affaire visible
        if business_id is None:
            project.estimations = self._collect_estimations(None, task_id=task_id)
            project.invoices = self._collect_invoices(None, task_id=task_id)

        # Quand le contexte est un devis sans affaire
        # (on a un task_id mais pas de business_id), on veut uniquemenet
        # les fichiers du projet et du devis
        # on ne veut donc aucune affaire dans le résultat,
        #
        # Dans les autres onglets fichiers
        # (dossiers, factures, affaires, devis avec affaire)
        # on veut lister la/les affaires concernées par le contexte
        # if le contexte n'est pas un devis sans affaire
        if not (task_id is not None and business_id is None):
            project.businesses = self._collect_businesses(business_id, task_id)

        return project

    def collection_get(
        self, business_id: Optional[int] = None, task_id: Optional[int] = None
    ) -> ProjectData:
        """Build the project tree data object"""
        return self._collect_project(business_id, task_id)

    def get_all_project_nodes(self) -> List[Node]:
        """Collect all the project related nodes (used by the zip files)"""
        result = (
            self.request.dbsession.query(Task)
            .filter(Task.project_id == self.project.id)
            .all()
        )
        result.extend(
            self.request.dbsession.query(Business)
            .filter(Business.project_id == self.project.id)
            .all()
        )
        result.append(self.project)
        return result

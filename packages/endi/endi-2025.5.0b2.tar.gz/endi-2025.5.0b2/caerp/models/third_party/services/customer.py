"""
Customer query service
"""
from caerp_base.models.base import DBSESSION
from .third_party import ThirdPartyService


class CustomerService(ThirdPartyService):
    @classmethod
    def get_tasks(cls, instance, type_str=None):
        from caerp.models.task import Task

        query = DBSESSION().query(Task)
        query = query.filter_by(customer_id=instance.id)
        if type_str is not None:
            query = query.filter(Task.type_ == type_str)
        return query

    @classmethod
    def count_tasks(cls, instance):
        return cls.get_tasks(instance).count()

    @classmethod
    def check_project_id(cls, customer_id, project_id):
        """
        Check that the given customer is attached to the given project
        """
        from caerp.models.project.project import ProjectCustomer

        return (
            DBSESSION()
            .query(ProjectCustomer)
            .filter_by(project_id=project_id)
            .filter_by(customer_id=customer_id)
            .count()
            > 0
        )

    @classmethod
    def get_project_ids(cls, customer):
        """
        Collect the ids of the projects attached to the given customer
        """
        from caerp.models.project.project import ProjectCustomer

        return [
            p.project_id
            for p in DBSESSION()
            .query(ProjectCustomer)
            .filter_by(customer_id=customer.id)
            .all()
        ]

    @classmethod
    def get_total_income(cls, instance, column_name="ht") -> int:
        from caerp.models.task import Task

        query = Task.total_income(column_name=column_name)
        return query.filter_by(customer_id=instance.id).scalar()

    @classmethod
    def get_total_estimated(cls, instance, column_name="ht") -> int:
        from caerp.models.task import Estimation

        query = Estimation.total_estimated(column_name=column_name)
        return query.filter_by(customer_id=instance.id).scalar()

    @classmethod
    def has_tva_on_margin_business(cls, instance):
        from caerp.models.task import Task
        from caerp.models.project.types import BusinessType
        from caerp.models.project.business import Business

        query = Task.query()
        query = query.join(Task.business)
        query = query.join(Business.business_type)
        query = query.filter(
            BusinessType.tva_on_margin == True,  # noqa: E712
            Task.customer_id == instance.id,
        )
        return DBSESSION.query(query.exists()).scalar()

    @classmethod
    def get_general_account(cls, instance, prefix=""):
        result = instance.compte_cg
        if not result:
            result = instance.company.get_general_customer_account(prefix)
        return result

    @classmethod
    def get_third_party_account(cls, instance, prefix=""):
        result = instance.compte_tiers
        if not result:
            result = instance.company.get_third_party_customer_account(prefix)
        return result

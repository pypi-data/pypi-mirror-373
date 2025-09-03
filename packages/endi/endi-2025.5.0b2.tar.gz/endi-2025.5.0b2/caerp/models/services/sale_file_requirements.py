"""
Service managing file requirements :

    Project

    Businesses

    Tasks (Invoice, Estimation, CancelInvoice)


Has several main responsabilities 

    - query requirement definitions
    - Populate the Indicators
    - Handle file events and update the indicators (with cascade)
       
"""
import logging
import typing
from zope.interface import implementer
from sqlalchemy.orm import load_only
from caerp_base.models.base import DBSESSION
from caerp.interfaces import IFileRequirementService
from caerp.models.project.file_types import BusinessTypeFileType
from caerp.models.indicators import SaleFileRequirement, Indicator

logger = logging.getLogger(__name__)


def build_indicator_from_requirement_def(
    business_type_file_type_req: BusinessTypeFileType, node: "Node"
) -> typing.Optional[SaleFileRequirement]:
    """
    Initialize an indicator from the given req definition object

    Handles dispatch of indicators on the upper levels

        - from Task to Business/Project
        - from Business to Project
    """
    from caerp.models.task import Task
    from caerp.models.project import Business

    requirement_type = business_type_file_type_req.requirement_type
    if isinstance(node, Task):
        if requirement_type == "business_mandatory":
            node = node.business
        elif requirement_type == "project_mandatory":
            node = node.project

    elif isinstance(node, Business) and requirement_type == "project_mandatory":
        node = node.project
    options = dict(
        file_type_id=business_type_file_type_req.file_type_id,
        validation=business_type_file_type_req.validation,
        doctype=business_type_file_type_req.doctype,
        requirement_type=requirement_type,
        node=node,
    )
    indicator = SaleFileRequirement.query().filter_by(**options).first()
    if indicator is None:
        indicator = SaleFileRequirement(**options)
        DBSESSION().add(indicator)
        DBSESSION().flush()

    return indicator


@implementer(IFileRequirementService)
class SaleFileRequirementService:
    @classmethod
    def populate(cls, node):
        """
        Generate SaleFileRequirement instances for the given node

        :param obj node: A :class:`caerp.models.node.Node` instance
        related to the sale module
        """
        business_type_id = node.business_type_id
        if business_type_id is None:
            raise Exception(
                "The provided Node instance %s has no business_type_id set" % node
            )

        business_file_req_defs = BusinessTypeFileType.get_file_requirements(
            business_type_id,
            node.type_,
        )

        for business_file_req_def in business_file_req_defs:
            build_indicator_from_requirement_def(business_file_req_def, node)

        return node

    @classmethod
    def _query_related_project_indicators(cls, node, file_type_id=None):
        query = SaleFileRequirement.query().filter_by(node_id=node.project_id)
        query = query.filter_by(doctype=node.type_)
        if file_type_id:
            query = query.filter_by(file_type_id=file_type_id)
        return query

    @classmethod
    def _get_related_project_indicators(cls, node, file_type_id=None):
        """
        Collect project indicators that concerns the current Node (Task/Business)
        """
        # On retrouve les requirements du projet qui concerne la
        # Task/Affaire courante
        return cls._query_related_project_indicators(node, file_type_id).all()

    @classmethod
    def _get_attached_indicators_status(cls, node) -> str:
        """
        Return the lowest status of attached SaleFileRequirement instances
        :param obj node: The node for which we check the indicators
        """
        query = DBSESSION().query(SaleFileRequirement.status)
        query = query.filter_by(node_id=node.id)
        query = query.distinct()
        result = [a[0] for a in query.all()]
        return Indicator.find_lowest_status(result)

    @classmethod
    def _get_related_project_indicators_status(cls, node) -> str:
        """
        Check if all indicators attached to the project and concerning this node
        are successfull
        """
        query = cls._query_related_project_indicators(node)
        result = [req.status for req in query]
        return Indicator.find_lowest_status(result)

    @classmethod
    def _get_invalid_indicators(cls, node) -> typing.List[SaleFileRequirement]:
        """
        Collect indicators attached to node that are not successfully validated
        """
        result = (
            SaleFileRequirement.query()
            .filter_by(node_id=node.id)
            .filter(SaleFileRequirement.status != SaleFileRequirement.SUCCESS_STATUS)
            .filter_by(forced=False)
        )
        return result.all()

    @classmethod
    def get_attached_indicators(cls, node, file_type_id=None):
        """
        Get all the indicators attached to the given node

        :param int node_id: The id of the node
        :param int file_type_id: The id of the file type
        """
        query = SaleFileRequirement.query().filter_by(node_id=node.id)
        if file_type_id is not None:
            query = query.filter_by(file_type_id=file_type_id)
        print(query.count())
        return query.all()

    @classmethod
    def get_related_indicators(cls, node, file_type_id=None):
        """Collect indicators related that concerns the given node"""
        # Par défaut on ne renvoie que ceux qui sont rattachés à l'objet courant
        return cls.get_attached_indicators(node, file_type_id)

    @classmethod
    def get_status(cls, node) -> str:
        return cls._get_attached_indicators_status(node)

    @classmethod
    def get_file_related_indicators(cls, file_id):
        """
        Return indicators related to the given file object
        """
        return SaleFileRequirement.query().filter_by(file_id=file_id).all()

    @classmethod
    def register(cls, node, file_object, action="add"):
        """
        Update the Indicators attached to node if one is matching the
        file_object

        :param obj node: A :class:`caerp.models.node.Node` instance
        related to the sale module
        :param obj file_object: A :class:`caerp.models.files.File` instance
        that has juste been uploaded
        :param str action: add/update/delete
        """
        if file_object.file_type_id:
            if action == "add":
                cls.on_file_add(node, file_object)
            elif action == "update":
                cls.on_file_update(node, file_object)
            elif action == "delete":
                cls.on_file_remove(node, file_object)

    @classmethod
    def on_file_add(cls, node, file_object):
        for indicator in cls.get_attached_indicators(node, file_object.file_type_id):
            indicator.set_file(file_object.id)

    @classmethod
    def on_file_update(cls, node, file_object):
        indicators = []
        for indicator in cls.get_attached_indicators(node, file_object.file_type_id):
            indicator.update_file(file_object.id)
            indicators.append(indicator)

        # Si le file_object a changé de type on doit nettoyer les anciens indicateurs
        for indicator in file_object.sale_file_requirements:
            if indicator not in indicators:
                indicator.remove_file()

    @classmethod
    def on_file_remove(cls, node, file_object):
        for indicator in cls.get_file_related_indicators(file_object.id):
            indicator.remove_file()

    @classmethod
    def force_all(cls, node):
        """
        Force all indicators that are not successfull

        :param obj node: The associated node
        """
        for indicator in cls._get_invalid_indicators(node):
            indicator.force()
            DBSESSION().merge(indicator)

    @classmethod
    def _check_project_files(cls, node):
        """
        Update file requirements regarding the project attached to the given
        node
        """
        if node.project is not None:
            files = node.project.files
            requirements = node.project.file_requirements
            for indicator in requirements:
                if indicator.doctype == node.type_:
                    for file_object in files:
                        if indicator.file_type_id == file_object.file_type_id:
                            indicator.set_file(file_object.id)


class TaskFileRequirementService(SaleFileRequirementService):
    @classmethod
    def _query_related_business_indicators(cls, node, file_type_id=None):
        query = SaleFileRequirement.query().filter_by(node_id=node.business_id)
        query = query.filter_by(doctype=node.type_)
        if file_type_id:
            query = query.filter_by(file_type_id=file_type_id)
        return query

    @classmethod
    def _get_related_business_indicators_status(cls, node) -> str:
        """ """
        query = cls._query_related_business_indicators(node).options(
            load_only(Indicator.status)
        )
        result = [req.status for req in query]
        return Indicator.find_lowest_status(result)

    @classmethod
    def _get_related_business_indicators(cls, node, file_type_id=None):
        """Collect business indicators that concerns the current Task"""
        # On retrouve les requirements de l'affaire qui concerne la Task courante
        query = cls._query_related_business_indicators(node, file_type_id)
        return query.all()

    @classmethod
    def get_related_indicators(cls, node, file_type_id=None):
        """Collect indicators that concerns the current Task"""
        indicators = cls.get_attached_indicators(node, file_type_id)
        indicators.extend(cls._get_related_business_indicators(node, file_type_id))
        indicators.extend(cls._get_related_project_indicators(node, file_type_id))
        return indicators

    @classmethod
    def get_other_attachments(cls, node):
        """
        List files that are attached to the node but not related to any indicator
        """
        return [
            file_object
            for file_object in node.files
            if not file_object.sale_file_requirements
        ]

    @classmethod
    def get_status(cls, node) -> str:
        result = [
            cls._get_attached_indicators_status(node),
            cls._get_related_business_indicators_status(node),
            cls._get_related_project_indicators_status(node),
        ]
        return Indicator.find_lowest_status(result)

    @classmethod
    def check_status(cls, node):
        cls._check_business_files(node)
        cls._check_project_files(node)
        return node

    @classmethod
    def _check_business_files(cls, task):
        """
        Update file requirements regarding the business attached to the given
        task
        """
        # On va parcourir l'affaire pour vérifier si elle contient déjà des fichiers
        # du même type que des requirements nouvellement créés
        requirements = task.business.file_requirements
        files = task.business.files
        for indicator in requirements:
            if indicator.doctype == task.type_:
                for file_object in files:
                    if file_object.file_type_id == indicator.file_type_id:
                        indicator.set_file(file_object.id)


class BusinessFileRequirementService(SaleFileRequirementService):
    """
    Manage Business file requirements
    """

    @classmethod
    def get_related_indicators(cls, node, file_type_id=None):
        indicators = cls.get_attached_indicators(node, file_type_id)
        indicators.extend(cls._get_related_project_indicators(node, file_type_id))
        indicators.extend(cls._get_children_indicators(node, file_type_id))
        return indicators

    @classmethod
    def _query_children_indicators(cls, node, file_type_id=None):
        """"""
        from caerp.models.task import Task

        query = (
            SaleFileRequirement.query()
            .join(Task, SaleFileRequirement.node_id == Task.id)
            .filter(Task.business_id == node.id)
        )
        if file_type_id:
            query = query.filter(SaleFileRequirement.file_type_id == file_type_id)
        query = query.order_by(Task.type_)
        return query

    @classmethod
    def _get_children_indicators(cls, node, file_type_id=None) -> list:
        """Renvoie les indicateurs des Task de l'affaire node"""
        return cls._query_children_indicators(node, file_type_id).all()

    @classmethod
    def _get_children_status(cls, node) -> str:
        query = cls._query_children_indicators(node)
        query = query.options(load_only(Indicator.status)).distinct()
        result = [req.status for req in query]
        return Indicator.find_lowest_status(result)

    @classmethod
    def get_status(cls, node) -> str:
        result = [
            cls._get_attached_indicators_status(node),
            cls._get_related_project_indicators_status(node),
            cls._get_children_status(node),
        ]
        return Indicator.find_lowest_status(result)

    @classmethod
    def check_status(cls, node):
        cls._check_project_files(node)
        return node


class ProjectFileRequirementService(SaleFileRequirementService):
    """
    Manage Project file requirements
    """

    @classmethod
    def get_related_indicators(cls, node, file_type_id=None):
        indicators = cls.get_attached_indicators(node, file_type_id)
        indicators.extend(cls._get_children_indicators(node, file_type_id))
        return indicators

    @classmethod
    def _query_children_indicators(cls, node, file_type_id=None):
        from caerp.models.project import Business
        from caerp.models.task import Task

        node_ids = [
            a[0]
            for a in DBSESSION()
            .query(Business.id)
            .filter(Business.project_id == node.id)
        ]
        node_ids.extend(
            [
                a[0]
                for a in DBSESSION().query(Task.id).filter(Task.project_id == node.id)
            ]
        )
        query = SaleFileRequirement.query().filter(
            SaleFileRequirement.node_id.in_(node_ids)
        )
        if file_type_id:
            query = query.filter(SaleFileRequirement.file_type_id == file_type_id)
        return query

    @classmethod
    def _get_children_indicators(cls, node, file_type_id=None):
        """Renvoie les indicateurs des Task et des affaires du projet node"""
        return cls._query_children_indicators(node, file_type_id).all()

    @classmethod
    def _get_children_indicators_status(cls, node):
        query = cls._query_children_indicators(node)
        query = query.options(load_only(Indicator.status)).distinct()
        result = [req.status for req in query]
        return Indicator.find_lowest_status(result)

    @classmethod
    def populate(cls, node):
        return node

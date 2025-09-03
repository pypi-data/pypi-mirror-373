"""
"""
import logging
import typing

from sqlalchemy import (
    Column,
    Integer,
    Boolean,
    ForeignKey,
    String,
)
from sqlalchemy.orm import (
    relationship,
)

from caerp_base.models.base import (
    DBBASE,
    DBSESSION,
    default_table_args,
)
from caerp_base.models.mixins import (
    TimeStampedMixin,
)


logger = logging.getLogger(__name__)


class Indicator(TimeStampedMixin, DBBASE):
    """
    Model recording computed statuses
    """

    __tablename__ = "indicator"
    __table_args__ = default_table_args
    __mapper_args__ = {
        "polymorphic_on": "type_",
        "polymorphic_identity": "indicator",
    }
    id = Column(Integer, primary_key=True)
    # danger / warning / success
    DANGER_STATUS = "danger"
    WARNING_STATUS = "warning"
    SUCCESS_STATUS = "success"
    STATUSES = (DANGER_STATUS, WARNING_STATUS, SUCCESS_STATUS)
    status = Column(String(20), default=DANGER_STATUS)

    VALID_STATUS = "valid"
    INVALID_STATUS = "invalid"
    WAIT_STATUS = "wait"
    DEFAULT_STATUS = "none"
    VALIDATION_STATUS = (
        INVALID_STATUS,
        VALID_STATUS,
        WAIT_STATUS,
        DEFAULT_STATUS,
    )
    # none / invalid / wait / valid
    validation_status = Column(String(20), default=DEFAULT_STATUS)
    forced = Column(Boolean(), default=False)
    type_ = Column(
        "type_",
        String(30),
        info={"colanderalchemy": {"exclude": True}},
        nullable=False,
    )

    @classmethod
    def find_lowest_status(cls, statuses: typing.List[str]) -> str:
        """Find the lowest status from a list of statuses"""
        result = [
            status for key in cls.STATUSES for status in statuses if status == key
        ]
        if len(result) >= 1:
            return result[0]
        return "success"

    def cmp_status(self, other_status):
        """
        Compare the current's instance status and the given one

        Return the the lowest status

        danger and danger = danger
        warning and danger = danger
        warning and success = warning
        danger and success = success

        :param str other_status: The status to compare to
        :returns: One of the availabe statuses
        :rtype: str
        """
        if self.STATUSES.index(self.status) < self.STATUSES.index(other_status):
            return self.status
        else:
            return other_status

    @property
    def main_status(self):
        """Compare the status and validation_status to return the most relevant one"""
        if self.validation_status == "none":
            return self.status
        else:
            return self.validation_status

    def force(self):
        self.forced = True
        self.status = "success"

    def unforce(self):
        self.forced = False
        self.set_default_status()

    def set_default_status(self):
        """
        Set the default status to a default 'danger'
        """
        self.status = "danger"

    @property
    def validated(self):
        return self.validation_status == "valid" or self.forced

    def set_validation_status(self, status):
        if status not in self.VALIDATION_STATUS:
            raise Exception("Invalid validation status")

        self.validation_status = status
        if status == "valid":
            self.status = "success"
        else:
            self.status = "warning"
        return DBSESSION.merge(self)

    def __json__(self, request):
        return dict(
            id=self.id,
            status=self.status,
            validation_status=self.validation_status,
            forced=self.forced,
        )


class CustomBusinessIndicator(Indicator):
    """
    Custom Indicator related to businesses with a label and a custom name
    """

    __tablename__ = "custom_indicator"

    __mapper_args__ = {"polymorphic_identity": "custom_indicator"}
    id = Column(ForeignKey("indicator.id"), primary_key=True)
    name = Column(String(255), nullable=False)
    label = Column(String(255), default="Indicateur")
    business_id = Column(ForeignKey("business.id", ondelete="cascade"))
    business = relationship(
        "Business",
        back_populates="indicators",
    )

    def get_company_id(self) -> int:
        return self.business.project.company_id


class SaleFileRequirement(Indicator):
    """
    Model recording File Requirements status
    """

    __tablename__ = "sale_file_requirement"

    __mapper_args__ = {"polymorphic_identity": "sale_file_requirement"}
    id = Column(ForeignKey("indicator.id"), primary_key=True)
    # Copied from the BusinessTypeFileType table
    file_type_id = Column(ForeignKey("file_type.id"))
    doctype = Column(String(14))
    requirement_type = Column(String(20))
    validation = Column(Boolean(), default=False)

    file_id = Column(ForeignKey("file.id"), nullable=True)
    node_id = Column(ForeignKey("node.id"))

    file_object = relationship(
        "File",
        primaryjoin="SaleFileRequirement.file_id==File.id",
        back_populates="sale_file_requirements",
    )
    node = relationship(
        "Node",
        primaryjoin="SaleFileRequirement.node_id==Node.id",
        back_populates="file_requirements",
    )
    file_type = relationship("FileType")

    def __init__(self, *args, **kwargs):
        Indicator.__init__(self, *args, **kwargs)
        self.set_default_status()
        self.set_default_validation_status()

    def set_default_status(self):
        """
        Set the default status regarding the requirement type
        """
        if self.requirement_type == "recommended":
            self.status = "warning"
        else:
            self.status = "danger"

    def set_default_validation_status(self):
        """
        Set the default validation status regarding the validation attribute
        """
        if not self.validation:
            self.validation_status = "valid"
        else:
            self.validation_status = "none"

    def merge_indicator(self, indicator):
        """
        Merge the given SaleFileRequirement with the current one

        if a file has been provided, we call the set_file method that handles
        the status
        if no file has been provided, the indicator may have been forced, we
        register that status

        :param obj indicator: an instance of the current class
        """
        result = self
        # on a un fichier
        if indicator.file_id is not None:
            result = self.set_file(
                indicator.file_id,
                validated=indicator.validated,
            )
            # on récupère l'état de validation du fichier déposé
            if indicator.validation == self.validation:
                self.validation_status = indicator.validation_status

        return result

    def update_status(self, validated=False):
        """Update an Indicator's status"""
        if not validated and self.validation:
            self.validation_status = self.WAIT_STATUS
            self.status = self.WARNING_STATUS
        else:
            self.status = "success"
        return DBSESSION().merge(self)

    def set_file(self, file_id, validated=False):
        """
        Attach a file_id to this indicator

        :param int file_id: An id of a file persisted to database
        :param bool validated: True if this file been validated in another
        indicator
        """
        self.file_id = file_id
        self.update_status(validated)
        return DBSESSION().merge(self)

    def update_file(self, file_id):
        """
        The file file_id was updated, we update the indicator if it was related
        to this file and if needed (if the current requirement needs validation)

        :param int file_id: An id of a file persisted to database
        :param bool validated: True if this file been validated in another
        indicator
        """
        # On a changer de fichier
        if file_id != self.file_id:
            self.set_file(file_id)
        else:
            # On a pas changé de fichier mais on a probablement changé les données
            # On doit mettre à jour le statut
            self.update_status()

        return DBSESSION().merge(self)

    def remove_file(self):
        """
        Remove file reference from this indicator
        """
        self.file_id = None
        self.set_default_status()
        self.set_default_validation_status()
        return DBSESSION().merge(self)

    @classmethod
    def get_by_type_id(cls, node_id, file_type_id):
        """
        Find the SaleFileRequirment with the given file_type_id and the given node_id
        """
        return (
            cls.query()
            .filter(cls.node_id == node_id)
            .filter(cls.file_type_id == file_type_id)
            .first()
        )

    def __json__(self, request):
        result = Indicator.__json__(self, request)
        if self.file_id:
            file_json = self.file_object.__json__(request)
        else:
            file_json = None
        result.update(
            dict(
                validation=self.validation,
                file_type_id=self.file_type_id,
                requirement_type=self.requirement_type,
                doctype=self.doctype,
                file_id=self.file_id,
                file_type=self.file_type.__json__(request),
                file_name=None,
                file_object=file_json,
                node_id=self.node_id,
            )
        )
        if self.file_id:
            result["file_name"] = self.file_object.name
        return result

    def get_company_id(self) -> int:
        if hasattr(self.node, "get_company_id"):
            return self.node.get_company_id()
        elif hasattr(self.node, "company_id"):
            return self.node.company_id
        else:
            return None

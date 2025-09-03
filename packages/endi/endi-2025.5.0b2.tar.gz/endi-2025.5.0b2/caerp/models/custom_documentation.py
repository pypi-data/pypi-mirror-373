import datetime
import logging
from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    String,
    Text,
    Date,
)
from sqlalchemy.orm import (
    relationship,
)
from caerp_base.models.base import (
    DBBASE,
    default_table_args,
)


log = logging.getLogger(__name__)


class CustomDocumentation(DBBASE):
    """
    Custom Help
    """

    __tablename__ = "custom_documentation"
    __table_args__ = default_table_args

    id = Column(Integer, primary_key=True)

    title = Column(
        String(255),
        nullable=False,
    )

    file_id = Column(
        ForeignKey("file.id", ondelete="CASCADE"),
    )

    uri = Column(Text)

    document = relationship(
        "File",
        primaryjoin="File.id==CustomDocumentation.file_id",
        cascade="all, delete",
    )

    updated_at = Column(
        Date(),
        info={
            "colanderalchemy": {
                "exclude": True,
                "title": "Mis(e) à jour le",
            }
        },
        nullable=False,
        default=datetime.date.today,
        onupdate=datetime.date.today,
    )

import datetime
import logging

from beaker.cache import cache_region
from sqlalchemy import (
    Integer,
    Column,
    ForeignKey,
    String,
    DateTime,
    Boolean,
    Table,
    Text,
    distinct,
    func,
)
from sqlalchemy.orm import (
    relationship,
    backref,
)
from caerp_base.models.base import (
    default_table_args,
    DBBASE,
    DBSESSION,
)
from caerp.models.activity import Event
from caerp.models.options import (
    ConfigurableOption,
    get_id_foreignkey_col,
)


log = logging.getLogger(__name__)

WORKSHOP_TAG_TO_WORKSHOP_REL_TABLE = Table(
    "workshop_tag_workshop_rel",
    DBBASE.metadata,
    Column(
        "workshop_tag_id",
        Integer,
        ForeignKey("workshop_tag_option.id", ondelete="cascade"),
    ),
    Column(
        "workshop_id",
        Integer,
        ForeignKey(
            "workshop.id", ondelete="cascade", name="fk_workshop_tag_workshop_rel_id"
        ),
    ),
    mysql_charset=default_table_args["mysql_charset"],
    mysql_engine=default_table_args["mysql_engine"],
)


WORKSHOP_TRAINER = Table(
    "workshop_trainer",
    DBBASE.metadata,
    Column(
        "workshop_id",
        Integer,
        ForeignKey("workshop.id", ondelete="cascade"),
        nullable=False,
    ),
    Column(
        "user_id",
        Integer,
        ForeignKey("accounts.id", ondelete="cascade"),
        nullable=False,
    ),
    mysql_charset=default_table_args["mysql_charset"],
    mysql_engine=default_table_args["mysql_engine"],
)


class WorkshopTagOption(ConfigurableOption):
    """
    Managing tags options
    """

    __colanderalchemy_config__ = {
        "title": "Étiquettes d’atelier",
        "description": "Configuration des étiquettes d’atelier disponibles",
        "validation_msg": "Les étiquettes d'atelier ont bien été configurées",
        "seq_widget_options": {
            "add_subitem_text_template": "Ajouter une étiquette",
            "min_len": 0,
        },
    }
    id = get_id_foreignkey_col("configurable_option.id")


class Workshop(Event):
    """
    A workshop model

    It's a meta event grouping a bunch of timeslots with each their own
    attendance sheet
    """

    __tablename__ = "workshop"
    __table_args__ = default_table_args
    __mapper_args__ = {"polymorphic_identity": "workshop"}
    id = Column(Integer, ForeignKey("event.id"), primary_key=True)
    info1_id = Column(ForeignKey("workshop_action.id"))
    info2_id = Column(ForeignKey("workshop_action.id"))
    info3_id = Column(ForeignKey("workshop_action.id"))
    info1 = relationship(
        "WorkshopAction",
        primaryjoin="Workshop.info1_id==WorkshopAction.id",
    )
    info2 = relationship(
        "WorkshopAction",
        primaryjoin="Workshop.info2_id==WorkshopAction.id",
    )
    info3 = relationship(
        "WorkshopAction",
        primaryjoin="Workshop.info3_id==WorkshopAction.id",
    )
    trainers = relationship(
        "User",
        secondary=WORKSHOP_TRAINER,
        info={
            "colanderalchemy": {
                "title": "Animateur(s)/ice(s)",
            },
            "export": {"exclude": True},
        },
    )
    tags = relationship(
        "WorkshopTagOption",
        secondary=WORKSHOP_TAG_TO_WORKSHOP_REL_TABLE,
        info={
            "export": {"related_key": "id"},
            "colanderalchemy": {
                "export": {"exclude": True},
            },
        },
    )
    description = Column(Text, default="")
    place = Column(Text, default="")
    max_participants = Column(Integer, default=0, nullable=False)
    company_manager_id = Column(ForeignKey("company.id"))
    company_manager = relationship(
        "Company",
        primaryjoin="Workshop.company_manager_id==Company.id",
    )

    @property
    def title(self):
        """
        Return a title for this given workshop
        """
        return "Atelier '{0}' animé par {1}".format(
            self.name, ", ".join(i.label for i in self.trainers)
        )

    def duplicate(self):
        new_item = Workshop(
            name="Copie de {}".format(self.name),
            tags=self.tags,
            description=self.description,
            place=self.place,
            max_participants=self.max_participants,
            _acl=self._acl,
            datetime=self.datetime,
            status=self.status,
            info1=self.info1,
            info2=self.info2,
            info3=self.info3,
            trainers=self.trainers,
            company_manager_id=self.company_manager_id,
            signup_mode=self.signup_mode,
            owner=self.owner,
        )

        for timeslot in self.timeslots:
            new_item.timeslots.append(timeslot.duplicate())

        for participant in self.participants:
            new_item.participants.append(participant)

        return new_item

    def relates_single_day(self):
        """
        Does the TimeSlots are all occuring the same day as Workshop.
        """
        for slot in self.timeslots:
            if (
                slot.start_time.date() != self.datetime.date()
                or slot.end_time.date() != self.datetime.date()
            ):
                return False
        return True

    def __str__(self):
        return "<Workshop : %s (%s)>" % (self.id, self.title)

    def get_company_id(self):
        """
        Usefull to get the current company if a workshop is the context
        """
        return self.company_manager_id


class Timeslot(Event):
    """
    A time slot for a given workshop
    """

    __tablename__ = "timeslot"
    __table_args__ = default_table_args
    __mapper_args__ = {"polymorphic_identity": "timeslot"}
    id = Column(Integer, ForeignKey("event.id"), primary_key=True)
    start_time = Column(DateTime())
    end_time = Column(DateTime())
    workshop_id = Column(ForeignKey("workshop.id"))

    workshop = relationship(
        "Workshop",
        primaryjoin="Timeslot.workshop_id==Workshop.id",
        backref=backref(
            "timeslots", order_by="Timeslot.start_time", cascade="all, delete-orphan"
        ),
    )

    @property
    def duration(self):
        time_delta = self.end_time - self.start_time
        hours, rest = divmod(time_delta.seconds, 3600)
        minutes, seconds = divmod(rest, 60)
        hours = 24 * time_delta.days + hours
        return hours, minutes

    def duplicate(self):
        timeslot = Timeslot(
            name=self.name,
            _acl=self._acl,
            datetime=self.datetime,
            status=self.status,
            start_time=self.start_time,
            end_time=self.end_time,
        )

        for participant in self.participants:
            timeslot.participants.append(participant)

        return timeslot


class WorkshopAction(DBBASE):
    __tablename__ = "workshop_action"
    __table_args__ = default_table_args
    id = Column(Integer, primary_key=True)
    label = Column(String(255))
    active = Column(Boolean(), default=True)
    parent_id = Column(ForeignKey("workshop_action.id"))
    children = relationship(
        "WorkshopAction",
        primaryjoin="WorkshopAction.id==WorkshopAction.parent_id",
        backref=backref("parent", remote_side=[id]),
        cascade="all",
    )


# Usefull queries
def get_workshop_years(kw=None):
    """
    Return a cached query for the years we have workshops in database

    :param kw: is here only for API compatibility
    """

    @cache_region("long_term", "workshopyears")
    def workshopyears():
        workshop_years = func.extract("YEAR", Workshop.datetime)
        query = DBSESSION().query(distinct(workshop_years))
        query = query.order_by(workshop_years)
        years = [year[0] for year in query]
        current = datetime.date.today().year
        if current not in years:
            years.append(current)
        return years

    return workshopyears()

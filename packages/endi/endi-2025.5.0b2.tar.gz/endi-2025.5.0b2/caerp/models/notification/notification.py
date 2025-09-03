import datetime
import logging
from typing import Optional
from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    String,
    ForeignKey,
    Date,
    Text,
    Boolean,
)
from sqlalchemy.orm import relationship, load_only

from caerp_base.models.base import (
    DBBASE,
    default_table_args,
)
from caerp_base.models.mixins import TimeStampedMixin
from caerp_base.models.types import JsonEncodedList

logger = logging.getLogger(__name__)


class NotificationChannel(DBBASE):
    """Notification channel names. Register all known Channels (allow third party
    libraries to register their own)"""

    __tablename__ = "notification_channel"
    __table_args__ = default_table_args
    id = Column(Integer, primary_key=True)
    name = Column(
        String(50),
        doc="Clé interne utilisée dans le code",
        unique=True,
        nullable=False,
    )
    label = Column(
        String(255),
        doc="Libellé (notamment pour l'admin)",
    )

    @classmethod
    def get_by_name(cls, name):
        return cls.query().filter(cls.name == name).first()


class NotificationEventType(DBBASE):
    """Type of notification that are fired by the application

    Third party libraries can add their own notifications type for which a channel
    can then be configured
    """

    __tablename__ = "notification_event_type"
    __table_args__ = default_table_args
    id = Column(Integer, primary_key=True)
    key = Column(
        String(100),
        doc="Clé interne utilisée dans le code lors de l'envoi des notifications",
        unique=True,
        nullable=False,
    )
    label = Column(
        String(255),
        doc="Libellé",
    )
    default_channel_name = Column(
        String(15),
        default="mail",
        doc="Channel à utiliser pour la publication (mail, message, "
        "alert, header_message)",
    )
    status_type = Column(
        String(15),
        default="neutral",
        doc="Type de notification (valid/success/error/neutral...)",
    )

    @classmethod
    def get_type(cls, key):
        return cls.query().filter_by(key=key).first()

    @classmethod
    def get_status_type(cls, key):
        instance = (
            cls.query().options(load_only("status_type")).filter_by(key=key).first()
        )
        result = "neutral"
        if instance is not None:
            result = instance.status_type
        return result


class NotificationEvent(DBBASE, TimeStampedMixin):
    """
    Planned notification that will be dispatched to end users after due_date

    Stores the notification information that will be used to issue the notifications

    Also stores a check query to verify it's still relevant
    """

    __tablename__ = "notification_event"
    __table_args__ = default_table_args
    id = Column(Integer, primary_key=True)
    key = Column(
        String(100),
        doc="Clé interne au logiciel (correspond à un type)",
    )
    title = Column(String(255), doc="Titre de la notification")
    body = Column(Text(), doc="Contenu de la notification (peut contenir du html)")
    due_datetime = Column(
        DateTime(),
        default=datetime.datetime.now,
        doc=(
            "Date et heures d'échéance à partir de laquelle les notifications doivent être "
            "publiées"
        ),
    )
    check_query = Column(
        Text(),
        nullable=True,
        doc=(
            "Requête de validité au format texte. L'event est annulé "
            "si la requête ne renvoie rien ou renvoie un résultat négatif (count(id)"
            " qui renverrai 0 par exemple)"
        ),
    )
    context_tablename = Column(
        String(255),
        nullable=True,
        doc=(
            "Nom de la table de l'objet auquel cette notification se réfère (permet de "
            "modifier la notification en cas d'edit/delete de l'élément)"
        ),
    )
    context_id = Column(
        Integer(),
        nullable=True,
        doc="Id de l'objet auquel cette notification se réfère",
    )
    group_names = Column(JsonEncodedList(), doc="Liste des groups destinataires")
    user_ids = Column(JsonEncodedList(), doc="Liste des ids des destinataires")
    account_type = Column(
        String(20),
        doc="Type de compte utilisateur (entrepreneur, equipe_appui)",
        nullable=True,
    )
    # N'est volontairement pas une relation
    company_id = Column(
        Integer(),
        doc="Id de l'enseigne de destination",
    )
    # Permet de forcer le channel de communication
    force_channel = Column(
        String(50),
        nullable=True,
        doc="Canal d'envoi de la notification (forcé à l'origine)",
    )
    # On stocke volontairement l'id du user et pas celui du référent car le référent à
    # la date d'émission de l'event n'est pas forcément celui au moment de la
    # génération de la notification
    follower_user_id = Column(
        Integer(), doc="Id de l'entrepreneur (on enverra le message à son référent)"
    )
    published = Column(
        Boolean(), default=False, doc="Les notifications ont-elles été publiées ?"
    )

    notifications = relationship(
        "Notification",
        cascade="all,delete,delete-orphan",
        back_populates="event",
        doc="Liste des notifications associées à cet évènement (permet de les supprimer "
        "si l'event n'est plus d'actualité)",
    )

    @classmethod
    def find_existing(
        cls, context_tablename: str, context_id: int
    ) -> Optional["NotificationEvent"]:
        """Find an existing NotificationEvent referring to the given context"""
        return (
            cls.query()
            .filter(
                cls.context_tablename == context_tablename, cls.context_id == context_id
            )
            .first()
        )

    def is_read(self, request):
        """check if all related notifications have been read"""
        if not self.published:
            return False
        elif not self.notifications:
            return True
        return (
            request.dbsession.query(Notification.id)
            .filter_by(event_id=self.id, read=False)
            .count()
            == 0
        )

    def is_valid(self, request):
        """
        Check if this notification should still be fired ?
        """
        if not self.check_query:
            return True
        try:
            query_result = request.dbsession.execute(self.check_query).first()
            result = True
            if query_result:
                if not query_result[0]:
                    result = False
            else:
                result = False
        except Exception:
            logger.exception("Erreur de syntaxe SQL ?")
            result = False

        return result


class Notification(DBBASE):
    __tablename__ = "notification"
    __table_args__ = default_table_args
    id = Column(Integer, primary_key=True)
    key = Column(
        String(100),
        doc="Type de notification",
    )
    title = Column(String(255), doc="Titre de la notification")
    body = Column(Text(), doc="Contenu de la notification (peut inclure du code html)")
    # Utilisé uniquement lorsque l'on repousse la notification (me le rappeler dans 15j)
    due_date = Column(
        Date(),
        default=datetime.date.today,
        doc="Date d'apparition de la notification (notamment si on la repousse dans "
        "le temps)",
    )
    read = Column(
        Boolean(),
        default=False,
        doc="Lu ?",
    )
    status_type = Column(
        String(15),
        default="neutral",
        doc="Type de notification (valid/success/error/neutral...)",
    )
    channel = Column(
        String(50),
        default="message",
        doc=(
            "Canal d'envoi de la notification parmi un des trois canaux internes "
            "(message->cloche, header_message->haut depage, alert->modale)"
        ),
    )
    user_id = Column(ForeignKey("accounts.id", ondelete="CASCADE"))
    user = relationship("User", back_populates="notifications")
    event_id = Column(ForeignKey("notification_event.id", ondelete="CASCADE"))
    event = relationship(NotificationEvent, back_populates="notifications")

    def __json__(self, request):
        return dict(
            id=self.id,
            key=self.key,
            title=self.title,
            body=self.body,
            due_date=self.due_date,
            user_id=self.user_id,
            status_type=self.status_type,
            channel=self.channel,
        )

    def postpone(self, request, deltadays: int = 7):
        """Move the notification's due_date"""
        self.due_date = datetime.date.today() + datetime.timedelta(days=deltadays)
        request.dbsession.merge(self)

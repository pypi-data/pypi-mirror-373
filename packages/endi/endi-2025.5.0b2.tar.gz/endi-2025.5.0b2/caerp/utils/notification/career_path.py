"""
Career Path related notification tools
"""
import logging
import datetime
import typing

from ..datetimes import format_long_date

from caerp.models.career_path import CareerPath
from caerp.models.notification.notification import NotificationEvent
from caerp.models.user import User
from caerp.utils.datetimes import date_to_datetime

from .abstract import AbstractNotification
from .notification import notify


logger = logging.getLogger(__name__)

NOTIFICATION_TITLE_TMPL = (
    "Le {career_path.career_stage.name} de {user.label} arrive à son terme"
)

NOTIFICATION_BODY_TMPL = """Le {career_path.career_stage.name} de {user.label} arrive
 à son terme le {date_label}. <br /><a class='btn btn-default' href='/users/{user.id}'
 title='Aller à la fiche de cet entrepreneur'>Voir sa fiche</a>"""

# Check qu'on a pas eu d'étape de parcours plus récente +
# que l'étape de parcours existe toujours
NOTIFICATION_CHECK_QUERY_TMPL = """
SELECT min(check2) from
(
    SELECT (count(id)=0) as check2 FROM career_path
        WHERE stage_type in ('exit', 'contract', 'amendment')
            AND userdatas_id={career_path.userdatas_id}
            AND (start_date > '{end_date_str}' OR end_date > '{end_date_str}')
            AND id!={career_path.id}
    UNION
    SELECT count(id) as check2 FROM career_path WHERE id={career_path.id}
) as t
"""


def get_checkcareer_path_last_query(career_path: CareerPath) -> str:
    """Build a string query to check if the given career_path is last one"""
    end_date_str = career_path.end_date.strftime("%Y-%m-%d")

    return NOTIFICATION_CHECK_QUERY_TMPL.format(
        career_path=career_path, end_date_str=end_date_str
    )


def get_existing_notification_event(
    career_path: CareerPath,
) -> typing.Optional[NotificationEvent]:
    """Find an existing event referring to this specific career_path"""
    return NotificationEvent.find_existing(career_path.__tablename__, career_path.id)


def should_notification_event_be_updated(
    career_path: CareerPath, event: NotificationEvent
) -> bool:
    """Check if the notification event should be updated"""
    return career_path.end_date != event.due_datetime


def update_notification_event(
    request, user: User, career_path: CareerPath, event: NotificationEvent
):
    """Update an existing notification event if needed"""
    sql_check_query: str = get_checkcareer_path_last_query(career_path)
    date_label: str = format_long_date(career_path.end_date)
    event.check_query = sql_check_query
    event.title = NOTIFICATION_TITLE_TMPL.format(career_path=career_path, user=user)
    event.body = NOTIFICATION_BODY_TMPL.format(
        career_path=career_path, user=user, date_label=date_label
    )
    request.dbsession.merge(event)


def get_abstract_notification(
    user: User, career_path: CareerPath
) -> AbstractNotification:
    sql_check_query: str = get_checkcareer_path_last_query(career_path)
    date_label: str = format_long_date(career_path.end_date)
    notification = AbstractNotification(
        key="userdatas:reminder",
        title=NOTIFICATION_TITLE_TMPL.format(career_path=career_path, user=user),
        body=NOTIFICATION_BODY_TMPL.format(
            career_path=career_path, user=user, date_label=date_label
        ),
        check_query=sql_check_query,
        context_tablename=career_path.__tablename__,
        context_id=career_path.id,
        due_datetime=date_to_datetime(career_path.end_date),
    )
    return notification


def notify_career_path_end_date(
    request, user: User, career_path: CareerPath, update=False
):
    """Notify the end of a career_path to a user's follower"""
    today = datetime.date.today()
    if not career_path.end_date or career_path.end_date <= today + datetime.timedelta(
        days=2
    ):
        return

    if update:
        event = get_existing_notification_event(career_path)
        if event is not None:
            if not should_notification_event_be_updated(career_path, event):
                # Pas d'update nécessaire
                return
            # update
            already_published = event.published
            if already_published:
                logger.debug("Suppression de Notification existantes")
                # Si il est déjà publié, on supprime les notifications existantes
                for notification in event.notifications:
                    request.dbsession.delete(notification)
                request.dbsession.flush()
                # On remet published à False car il sera (re) publié à la date
                # d'échéance
                event.published = False
            logger.debug("Update d'une NotificationEvent existante")
            update_notification_event(request, user, career_path, event)
            return

    # add
    notification = get_abstract_notification(user, career_path)
    logger.debug("Planification d'une notification à échéance")
    notify(request, notification, follower_user_id=user.id)

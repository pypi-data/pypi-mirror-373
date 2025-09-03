import datetime

from paginate_sqlalchemy import SqlalchemyOrmPage
from sqlalchemy import desc

from caerp import resources
from caerp.models.activity import (
    Event,
    Attendance,
    Activity,
)
from caerp.models.workshop import Timeslot
from caerp.panels.company_index import utils


def _user_events_query(user_ids):
    """
    Return a sqla query for the user's events
    """
    if not isinstance(user_ids, (tuple, list)):
        user_ids = [user_ids]

    query = Event.query().with_polymorphic([Timeslot, Activity])
    query = query.filter(Event.type_.in_(["timeslot", "activity"]))
    query = query.filter(Event.attendances.any(Attendance.account_id.in_(user_ids)))
    query = query.filter(Event.datetime >= datetime.datetime.now())
    query = query.order_by(desc(Event.datetime))
    return query


def coming_events_panel(context, request):
    """
    Return the list of the upcoming events
    """
    if not request.is_xhr:
        resources.event_list_js.need()

    current_user = request.identity
    if current_user in context.employees:
        query = _user_events_query(request.identity.id)
        title = "Mes événements à venir"
    else:
        query = _user_events_query([u.id for u in context.employees])
        title = "Prochains événements de l'enseigne"

    page_nb = utils.get_page_number(request, "events_page_nb")
    items_per_page = utils.get_items_per_page(request, "events_per_page")

    paginated_events = SqlalchemyOrmPage(
        query,
        page_nb,
        items_per_page=items_per_page,
        url_maker=utils.make_get_list_url("events"),
    )

    result_data = {"events": paginated_events, "title": title}
    return result_data


def includeme(config):
    config.add_panel(
        coming_events_panel,
        "company_coming_events",
        renderer="panels/company_index/coming_events.mako",
    )

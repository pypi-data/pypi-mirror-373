"""
User connections listing views
"""
import logging
import colander
import datetime
from caerp.consts.permissions import PERMISSIONS
from caerp_base.models.base import DBSESSION
from caerp.models.user.user import User
from caerp.models.user.login import UserConnections
from caerp.forms.user.user import get_connections_schema
from caerp.views import BaseListView
from caerp.views.user.routes import USER_URL
from caerp.utils.widgets import ViewLink

logger = logging.getLogger(__name__)


class UserConnectionsListView(BaseListView):
    title = "Historique des connexions utilisateurs"
    schema = get_connections_schema()
    default_sort = "lastname"
    sort_columns = dict(
        lastname=User.lastname,
        firstname=User.firstname,
        email=User.email,
        month_last_connection=UserConnections.month_last_connection,
    )

    def populate_actionmenu(self, appstruct):
        self.request.actionmenu.add(
            ViewLink("Retour à l'annuaire des utilisateurs", path=USER_URL)
        )

    def query(self):
        """
        Return the main query for our list view
        """
        query = DBSESSION().query(UserConnections)
        query = query.join(User)
        query = query.filter(User.special == 0)
        return query

    def filter_year(self, query, appstruct):
        year = appstruct["year"]
        if year and year not in (-1, colander.null):
            query = query.filter(UserConnections.year == year)
            self.year = year
        else:
            self.year = datetime.date.today().year
        return query

    def filter_month(self, query, appstruct):
        month = appstruct["month"]
        if month and month not in (-1, colander.null, "-1"):
            query = query.filter(UserConnections.month == month)
            self.month = month
        else:
            self.month = datetime.date.today().month
        return query

    def more_template_vars(self, response_dict):
        """
        Add template datas in the response dictionnary
        """
        response_dict["selected_month"] = int(self.month)
        response_dict["selected_year"] = int(self.year)
        return response_dict


def includeme(config):
    """
    Pyramid module entry point

    :param obj config: The pyramid configuration object
    """
    config.add_view(
        UserConnectionsListView,
        route_name="/users/connections",
        renderer="/user/connections.mako",
        permission=PERMISSIONS["global.create_user"],
    )

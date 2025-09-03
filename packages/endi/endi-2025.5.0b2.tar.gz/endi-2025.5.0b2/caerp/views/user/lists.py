"""
User and user datas listing views
"""
import logging
import colander

from caerp.consts.permissions import PERMISSIONS
from sqlalchemy import (
    or_,
    distinct,
)
from caerp_base.models.base import DBSESSION
from caerp.models.company import (
    Company,
    CompanyActivity,
)
from caerp.models.user.user import User
from caerp.models.user.login import Login
from caerp.models.user.group import Group
from caerp.forms.user.user import get_list_schema
from caerp.utils.widgets import Link
from caerp.views import BaseListView


logger = logging.getLogger(__name__)


class UserFilterTools:
    def filter_name_search(self, query, appstruct):
        search = appstruct["search"]
        if search:
            query = query.filter(
                or_(
                    User.lastname.like("%" + search + "%"),
                    User.firstname.like("%" + search + "%"),
                    User.companies.any(Company.name.like("%" + search + "%")),
                    User.companies.any(Company.goal.like("%" + search + "%")),
                    User.login.has(Login.login.like("%" + search + "%")),
                )
            )

        return query

    def filter_antenne_id(self, query, appstruct):
        antenne_id = appstruct.get("antenne_id")
        if antenne_id not in (None, colander.null):
            if antenne_id == -2:
                # -2 means no antenne configured
                query = query.filter(User.companies.any(Company.antenne_id == None))
            else:
                query = query.filter(
                    User.companies.any(Company.antenne_id == antenne_id)
                )
        return query

    def filter_follower_id(self, query, appstruct):
        follower_id = appstruct.get("follower_id")
        if follower_id not in (None, colander.null):
            if follower_id == -2:
                # -2 means no follower configured
                query = query.filter(User.companies.any(Company.follower_id == None))
            else:
                query = query.filter(
                    User.companies.any(Company.follower_id == follower_id)
                )
        return query

    def filter_activity_id(self, query, appstruct):
        activity_id = appstruct.get("activity_id")
        if activity_id:
            query = query.filter(
                User.companies.any(
                    Company.activities.any(CompanyActivity.id == activity_id)
                )
            )
        return query

    def filter_user_group(self, query, appstruct):
        group_id = appstruct.get("group_id")
        if group_id:
            query = query.filter(User.login.has(Login.groups.any(Group.id == group_id)))
        return query

    def filter_user_account_type(self, query, appstruct):
        account_type = appstruct.get("account_type")
        if account_type and account_type != "all":
            query = query.filter(Login.account_type == account_type)
        return query


class BaseUserListView(UserFilterTools, BaseListView):
    """
    Base list for the User model
    Provide :

        The base User class query
        The filtering on the search field
        The filtering on the company activity_id

    add filters to specify more specific list views (e.g: trainers, users with
    account ...)
    """

    title = "Tous les comptes"
    schema = None
    sort_columns = dict(
        name=User.lastname,
        email=User.email,
    )
    add_template_vars = ("stream_actions",)

    def query(self):
        query = DBSESSION().query(distinct(User.id), User)
        query = query.outerjoin(User.companies)
        return query.filter(User.id > 0)

    def stream_actions(self, item):
        """
        Compile the action description for the given item
        """
        yield Link(
            self.request.route_path(
                "/users/{id}",
                id=item.id,
            ),
            "",
            title="Voir le compte",
            icon="pen",
            css="icon only",
        )
        if self.request.has_module("accompagnement") and self.request.has_permission(
            PERMISSIONS["global.manage_activity"]
        ):
            yield Link(
                self.request.route_path(
                    "activities", _query={"action": "new", "user_id": item.id}
                ),
                "",
                title="Nouveau rendez-vous",
                icon="calendar-plus",
                css="icon only",
            )


class GeneralAccountList(BaseUserListView):
    """
    List the User models with Login attached to them
    """

    sort_columns = dict(
        name=User.lastname,
        email=User.email,
    )

    def get_schema(self):
        admin = self.request.has_permission(PERMISSIONS["global.access_ea"])
        return get_list_schema(admin=admin)

    def filter_login_filter(self, query, appstruct):
        """
        Filter the list on accounts with login only
        """
        query = query.join(User.login)
        login_filter = appstruct.get("login_filter", "active_login")
        if login_filter == "active_login":
            query = query.filter(Login.active == True)  # NOQA : E712
        elif login_filter == "unactive_login":
            query = query.filter(Login.active == False)  # NOQA : E712
        return query


def includeme(config):
    """
    Pyramid module entry point

    :param obj config: The pyramid configuration object
    """
    config.add_view(
        GeneralAccountList,
        route_name="/users",
        renderer="/user/lists.mako",
        permission=PERMISSIONS["global.authenticated"],
    )

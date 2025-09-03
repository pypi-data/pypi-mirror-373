"""
    Index view
"""
import logging
from pyramid.httpexceptions import HTTPFound
from sqlalchemy import select, func
from caerp.consts.permissions import PERMISSIONS
from caerp.models.company import Company
from caerp.views.company.routes import DASHBOARD_ROUTE

log = logging.getLogger(__name__)


def index(request):
    """
    Index page
    """
    user = request.identity
    companies = user.active_companies
    if (
        request.dbsession.execute(
            select(func.count(Company.id)).filter(Company.active == True)
        ).scalar_one()
        == 1
    ):
        company_id = request.dbsession.execute(
            select(Company.id).filter(Company.active == True)
        ).scalar_one()
        return HTTPFound(request.route_path(DASHBOARD_ROUTE, id=company_id))

    if request.has_permission(PERMISSIONS["global.access_ea"]):
        return HTTPFound(request.route_path("manage"))
    elif len(companies) == 1:
        company = companies[0]
        href = request.route_path(DASHBOARD_ROUTE, id=company.id)
        return HTTPFound(href)
    else:
        for company in companies:
            company.url = request.route_path(DASHBOARD_ROUTE, id=company.id)
        return dict(title="Bienvenue dans enDI", companies=user.active_companies)


def includeme(config):
    """
    Adding the index view on module inclusion
    """
    config.add_route("index", "/")
    config.add_view(
        index,
        route_name="index",
        renderer="index.mako",
        permission=PERMISSIONS["global.authenticated"],
    )

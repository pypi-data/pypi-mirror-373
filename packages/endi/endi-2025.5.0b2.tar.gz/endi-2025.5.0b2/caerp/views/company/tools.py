import os
from .routes import ITEM_ROUTE


def get_company_url(request, company=None, subpath=None, api=False, **kwargs):
    """
    Build an url to access company views
    """
    route_path = ITEM_ROUTE

    if subpath:
        if subpath.startswith("/"):
            subpath = subpath[1:]
        route_path = os.path.join(route_path, subpath)
    if company:
        company_id = company.id
    else:
        company_id = request.context.id

    if api:
        route_path = f"/api/v1{route_path}"
    return request.route_path(route_path, id=company_id, _query=kwargs)

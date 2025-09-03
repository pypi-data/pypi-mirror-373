"""
    Json API views
    DEPRECATED 
"""

from caerp.consts.permissions import PERMISSIONS
from caerp.views.third_party.customer.routes import CUSTOMER_ITEM_ROUTE


def json_model_view(request):
    """
    Return a json representation of a model
    """
    return request.context


def includeme(config):
    """
    Configure the views for this module
    """
    config.add_view(
        json_model_view,
        route_name="/companies/{id}",
        renderer="json",
        request_method="GET",
        permission=PERMISSIONS["company.view"],
    )

    for route_name in "project", CUSTOMER_ITEM_ROUTE:
        config.add_view(
            json_model_view,
            route_name=route_name,
            renderer="json",
            request_method="GET",
            permission=PERMISSIONS["company.view"],
        )

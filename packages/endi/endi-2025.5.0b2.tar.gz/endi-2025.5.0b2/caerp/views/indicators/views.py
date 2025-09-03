import logging
from caerp.consts.permissions import PERMISSIONS
from pyramid.httpexceptions import HTTPFound
from caerp.views.indicators.controller import IndicatorController
from .routes import INDICATOR_ROUTE


logger = logging.getLogger(__name__)


def force_indicator_view(context, request):
    """
    Force an indicator (sets forced to True
    """
    controller = IndicatorController(request, context)
    controller.force()
    return HTTPFound(request.referrer)


def validate_file_view(context, request):
    """ """
    validation_status = request.GET.get("validation_status")
    controller = IndicatorController(request, context)
    controller.validate(validation_status)
    return HTTPFound(request.referrer)


def includeme(config):
    config.add_view(
        force_indicator_view,
        route_name=INDICATOR_ROUTE,
        permission=PERMISSIONS["context.force_indicator"],
        request_param="action=force",
    )
    config.add_view(
        validate_file_view,
        route_name=INDICATOR_ROUTE,
        permission=PERMISSIONS["context.validate_indicator"],
        request_param="action=validation_status",
    )

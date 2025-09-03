import logging

from caerp.models.project.project import Project
from caerp.models.project.business import Business
from caerp.models.task import Estimation, Invoice, CancelInvoice
from caerp.models.indicators import (
    CustomBusinessIndicator,
    SaleFileRequirement,
)


logger = logging.getLogger(__name__)


class IndicatorChanged:
    """
    Fired when an indicator is forced or if it has a status and the status was set
    """

    def __init__(self, request, indicator):
        self.request = request
        self.indicator = indicator


def on_indicator_change(event):
    logger.debug("On indicator change")
    if isinstance(event.indicator, SaleFileRequirement):
        logger.debug("The indicator is a SaleFileRequirement")
        node = event.indicator.node
        if isinstance(node, Business):
            businesses = [node]
        elif isinstance(node, (Estimation, Invoice, CancelInvoice)):
            businesses = [node.business]
        elif isinstance(node, Project):
            businesses = node.businesses
        else:
            raise Exception("Unexpected {}".format(type(event.indicator.node)))
        for business in businesses:
            business.status_service.update_status(business)
    elif isinstance(event.indicator, CustomBusinessIndicator):
        logger.debug("The indicator is a CustomBusinessIndicator")
        business = event.indicator.business
        business.status_service.update_status(business)


def includeme(config):
    config.add_subscriber(on_indicator_change, IndicatorChanged)

"""
Indicators REST view, scoped to node

.. http:get:: /api/v1/nodes/:node_id/indicators

    The indicators concerning the provided node

    :query scoped: Only indicators directly attached to the node will be returned,
                    if not provided, all indicators will be returned (event those
                    attached to upper levels in the hierarchy)

.. http:get:: /api/v1/indicators/:id

    Return a specific indicator in json format

.. http:put:: /api/v1/indicators/:id

    Edit a given indicator

    :query forced: Force the indicator
    :query validation_status: Set the validation status of the indicator

"""

import logging
from caerp.consts.permissions import PERMISSIONS
from typing import Optional
from caerp.utils.rest.parameters import LoadOptions
from caerp.views import BaseRestView
from caerp.models.node import Node
from caerp.models.indicators import Indicator, SaleFileRequirement
from caerp.views.indicators.routes import (
    INDICATOR_ITEM_API_ROUTE,
    INDICATOR_NODE_COLLECTION_API_ROUTE,
)
from .controller import IndicatorController

logger = logging.getLogger(__name__)


class IndicatorRestView(BaseRestView):
    def __init__(self, context, request=None):
        super().__init__(context, request)
        self.controller = IndicatorController(self.request, self.context)

    def get_node(self):
        if isinstance(self.context, Node):
            return self.context
        else:
            return self.context.node

    def _get_business_type_id(self, node: Node) -> Optional[int]:
        result = getattr(node, "business_type", None)
        if result is not None:
            return result.id
        else:
            return None

    def json_repr(self, req: SaleFileRequirement) -> dict:
        result: dict = req.__json__(self.request)
        btype_id = self._get_business_type_id(self.get_node())
        if btype_id is not None and req.file_type.get_template_id(btype_id) is not None:
            result["has_template"] = True
        return result

    def collection_get(self):
        params = LoadOptions.from_request(self.request)
        logger.debug("Loading indicators for node %s", self.get_node().id)
        logger.debug(params)
        return [self.json_repr(item) for item in self.controller.collection_get(params)]

    def force_view(self):
        return self.json_repr(self.controller.force())

    def validate_view(self):
        validation_status = self.get_posted_data().get("validation_status", None)
        return self.json_repr(self.controller.validate(validation_status))

    def format_item_result(self, model) -> dict:
        """Return the object returned by the get call"""
        result = model.__json__(self.request)
        return result


def includeme(config):
    config.add_rest_service(
        IndicatorRestView,
        route_name=INDICATOR_ITEM_API_ROUTE,
        collection_route_name=INDICATOR_NODE_COLLECTION_API_ROUTE,
        collection_context=Node,
        context=Indicator,
        collection_view_rights=PERMISSIONS["company.view"],  # Context is a node
        view_rights=PERMISSIONS["context.view_indicator"],
    )
    config.add_view(
        IndicatorRestView,
        attr="force_view",
        route_name=INDICATOR_ITEM_API_ROUTE,
        request_method="PUT",
        request_param="action=force",
        renderer="json",
        context=Indicator,
        permission=PERMISSIONS["context.force_indicator"],
    )
    config.add_view(
        IndicatorRestView,
        attr="validate_view",
        route_name=INDICATOR_ITEM_API_ROUTE,
        request_method="PUT",
        request_param="action=validation_status",
        renderer="json",
        context=Indicator,
        permission=PERMISSIONS["context.validate_indicator"],
    )

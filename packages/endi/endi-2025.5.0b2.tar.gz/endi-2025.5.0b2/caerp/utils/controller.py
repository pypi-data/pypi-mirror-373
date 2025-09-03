import logging
from typing import List

logger = logging.getLogger(__name__)


class ModelSerializeManager:
    def __init__(self, request):
        self.request = request
        self.dbsession = request.dbsession

    def serialize(self, item, item_dict: dict, fields: List[str]):
        for field in fields:
            if hasattr(item, field):
                item_dict[field] = getattr(item, field)
            else:
                logger.error(f"Error in {self} no field named {field}")
        return item_dict


class RelatedAttrManager:
    def __init__(self, request):
        self.request = request
        self.dbsession = request.dbsession

    def add_related(self, item, item_dict: dict, related: List[str]) -> dict:
        for value in related:
            method_name = "_add_related_{}".format(value)
            method = getattr(self, method_name, None)
            if method:
                method(item, item_dict)
            else:
                logger.error(
                    "Error in {}, no method named {}".format(self, method_name)
                )
        return item_dict


class BaseAddEditController:
    """Base class for building an add edit controller"""

    field_serializer_factory = ModelSerializeManager
    related_manager_factory = RelatedAttrManager

    def __init__(
        self,
        request,
        edit=False,
    ):
        self.request = request
        self.context = request.context
        self.edit = edit
        self._schema = None
        self._cache = {}
        self.field_serializer = self.field_serializer_factory(self.request)
        self.related_manager = self.related_manager_factory(self.request)

    def to_json(self, instance) -> dict:
        result = {}
        if "fields" in self.request.params:
            fields = self.request.params.getall("fields")
            result = self.field_serializer.serialize(instance, result, fields)
        if "related" in self.request.params:
            related_fields = self.request.params.getall("related")
            result = self.related_manager.add_related(instance, result, related_fields)

        if not result:
            result = instance.__json__(self.request)
        return result

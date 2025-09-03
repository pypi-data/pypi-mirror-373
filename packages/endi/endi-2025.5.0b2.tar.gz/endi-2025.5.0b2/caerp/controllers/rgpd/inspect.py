"""
Outil générique d'anonymisation de données RGPD

En ajoutant 

.. code-block:: python

    class MyModel(DBBASE):
        ...

        my_attribute = Column(
          String(55), nullable=True, info={"anonymize: True}
        )

On peut alors facilement anonymiser une instance de MyModel :

.. code-block:: python

    inspector = get_inspector(MyModel)
    inspector.anonymize(request, my_model_instance)

L'anonymisation set les valeurs à 0. 
Pour tout autre fonctionnement, il faut effectuer un traitement spécifique
"""
import logging
from sqlalchemy.orm.interfaces import ONETOMANY
from sqlalchemy.orm import (
    RelationshipProperty,
)
from sqla_inspect.base import BaseSqlaInspector
from caerp.models.user.userdatas import UserDatas


logger = logging.getLogger(__name__)


class Column(dict):
    """
    The column object wrapping the model's attribute

    key

        The attribute name

    label

        The attribute display label

    nullable

        The attribute can be null

    type

        attribute/relationship (relationship only for one to many rels)
        Allows to know how to anonymize the value
    """

    def set_value(self, request, instance):
        if self["type"] == "attribute":
            if not self["nullable"]:
                value = ""
            else:
                value = None
            setattr(instance, self["key"], value)
        elif self["type"] == "relationship":
            related = getattr(instance, self["key"], None)
            if related:
                if isinstance(related, list):
                    for item in related:
                        request.dbsession.delete(item)
                else:
                    request.dbsession.delete(related)


class AnonymizeInspector(BaseSqlaInspector):
    """
    A sqla inspector made for anonymization

    model

        The model we want to inspect

    excludes

        The name of the attributes we want to exclude from inspection

    exclude_relationships

        Should we exclude relationships (usefull for limiting recursive
        inspection)



    >>> inspector = get_inspector(UserDatas)
    >>> inspector.anonymize(request, userdata)
    """

    config_key = "anonymize"

    def __init__(self, model, excludes=(), exclude_relationships=False):
        BaseSqlaInspector.__init__(self, model)
        self.model = model
        self.excludes = excludes
        self.exclude_relationships = exclude_relationships
        self.columns = self._collect_columns()

    def _get_label(self, colanderalchemy_infos, stats_infos, key):
        if "label" in stats_infos:
            return stats_infos["label"]
        else:
            return colanderalchemy_infos.get("title", key)

    def _collect_columns(self):
        """
        Collect the columns used for anonymization
        """
        result = []

        for prop in self.get_sorted_columns():
            if prop.key in self.excludes:
                continue
            info_dict = self.get_info_field(prop)
            colanderalchemy_infos = info_dict.get("colanderalchemy", {})
            stats_infos = info_dict.get("export", {}).get("stats", {}).copy()

            if not info_dict.get("anonymize", False):
                continue
            ui_label = self._get_label(colanderalchemy_infos, stats_infos, prop.key)
            section = colanderalchemy_infos.get("section", "")
            if section:
                ui_label = "{0} : {1}".format(section, ui_label)

            column = Column({"key": prop.key, "label": ui_label})

            if isinstance(prop, RelationshipProperty):
                if prop.direction == ONETOMANY:
                    column["type"] = "relationship"
                else:
                    column["type"] = "attribute"
            else:
                nullable = prop.columns[0].nullable
                column["type"] = "attribute"
                column["nullable"] = nullable
            result.append(column)

        return result

    def anonymize(self, request, instance):
        for column in self.columns:
            column.set_value(request, instance)
        return instance


def get_inspector(model=UserDatas):
    """
    Return a anonymization inspector for the given model
    """
    return AnonymizeInspector(
        model,
        excludes=(
            "parent_id",
            "children",
            "type_",
            "_acl",
            "id",
            "parent",
        ),
    )

"""
    Models for work unit (days, ...)
"""
from typing import Optional

from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import Integer

from caerp.models.task.services.unity import WorkUnitService
from caerp_base.models.base import default_table_args
from caerp_base.models.base import DBBASE
from caerp.forms import (
    get_hidden_field_conf,
)


class WorkUnit(DBBASE):
    """
    Work unit, used to build the price list
    """

    __colanderalchemy_config__ = {
        "title": "Unités de prestation",
        "description": "",
        "help_msg": "Configurer les unités de prestation proposées dans les \
formulaires d'édition des devis/factures.\n Vous pouvez les réordonner par \
glisser-déposer.",
        "validation_msg": "Les unités de prestation ont bien été configurées",
        "seq_widget_options": {
            "add_subitem_text_template": "Ajouter une unité de prestation"
        },
    }
    __tablename__ = "workunity"
    __table_args__ = default_table_args
    id = Column(
        Integer,
        primary_key=True,
        info={"colanderalchemy": get_hidden_field_conf()},
    )
    label = Column(
        String(100),
        info={"colanderalchemy": {"title": "Intitulé"}},
        nullable=False,
    )
    order = Column(
        Integer,
        nullable=False,
        default=0,
        info={"colanderalchemy": get_hidden_field_conf()},
    )

    _caerp_service = WorkUnitService

    @classmethod
    def get_by_label(
        cls, label: str, case_sensitive: bool = False
    ) -> Optional["WorkUnit"]:
        return cls._caerp_service.get_by_label(cls, label, case_sensitive)

    def __json__(self, request):
        return dict(id=self.id, label=self.label, value=self.label)

    @classmethod
    def query(cls, *args):
        query = super(WorkUnit, cls).query(*args)
        query = query.order_by("order")
        return query

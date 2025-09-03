"""
    Model for career stages
"""
import deform
import deform_extensions
from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Boolean,
)
from sqlalchemy.orm import relationship
from caerp.models.tools import get_excluded_colanderalchemy
from caerp_base.models.base import (
    DBBASE,
    default_table_args,
)

STAGE_TYPE_OPTIONS = (
    (
        "",
        "Autre",
    ),
    (
        "entry",
        "Entrée CAE",
    ),
    (
        "contract",
        "Contrat de travail",
    ),
    (
        "amendment",
        "Avenant contrat de travail",
    ),
    (
        "exit",
        "Sortie CAE",
    ),
)

CAREER_STAGE_GRID = (
    (("active", 12),),
    (("name", 12),),
    (("cae_situation_id", 12),),
    (("stage_type", 12),),
)


class CareerStage(DBBASE):
    """
    Different career stages
    """

    __colanderalchemy_config__ = {
        "validation_msg": "Les étapes de parcours ont bien été configurées",
        "widget": deform_extensions.GridFormWidget(named_grid=CAREER_STAGE_GRID),
    }
    __tablename__ = "career_stage"
    __table_args__ = default_table_args
    id = Column(
        "id",
        Integer,
        primary_key=True,
        info={"colanderalchemy": {"widget": deform.widget.HiddenWidget()}},
    )
    active = Column(
        Boolean(),
        default=True,
        info={"colanderalchemy": {"exclude": True}},
    )
    name = Column(
        "name",
        String(100),
        nullable=False,
        info={"colanderalchemy": {"title": "Libellé de l'étape"}},
    )
    cae_situation_id = Column(
        ForeignKey("cae_situation_option.id"),
        info={
            "colanderalchemy": {
                "title": "Nouvelle situation dans la CAE",
                "description": "Lorsque cette étape sera affectée à un \
entrepreneur cette situation lui sera automatiquement attribuée",
            },
            "export": {"exclude": True},
        },
    )
    cae_situation = relationship(
        "CaeSituationOption",
        primaryjoin="CaeSituationOption.id==CareerStage.cae_situation_id",
        info={
            "colanderalchemy": get_excluded_colanderalchemy("Situation dans la CAE"),
            "export": {"related_key": "label"},
        },
    )
    stage_type = Column(
        String(15),
        info={
            "colanderalchemy": {"title": "Nature"},
            "export": {
                "formatter": lambda val: dict(STAGE_TYPE_OPTIONS).get(val),
                "stats": {"options": STAGE_TYPE_OPTIONS},
            },
        },
    )

    @classmethod
    def query(cls, include_inactive=False):
        q = super(CareerStage, cls).query()
        if not include_inactive:
            q = q.filter(CareerStage.active == True)
        return q.order_by("name")

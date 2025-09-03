import logging

import colander
from sqlalchemy import (
    Column,
    Date,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    Boolean,
)

from caerp_base.models.base import (
    default_table_args,
)
from caerp.forms.validators import validate_rncp_rs_code
from .services import (
    SaleProductTrainingService,
    SaleProductVAEService,
)
from .work import SaleProductWork

logger = logging.getLogger(__name__)


PRESENCE_MODALITY_OPTIONS = [
    ("physical", "Présenciel"),
    ("remote", "Distanciel"),
    ("blended", "Blended (mixte)"),
]

PRESENCE_MODALITY_MAP = dict(PRESENCE_MODALITY_OPTIONS)

GROUP_SIZES_OPTIONS = [
    ("individual", "Individuel"),
    ("group", "Groupe"),
]
GROUP_SIZES_MAP = dict(GROUP_SIZES_OPTIONS)


class BaseQualiopiSaleProduct(SaleProductWork):
    """
    Base model for Formation / VAE / Bilan de compétences

    Which are the three action types  covered by QUALIOPI referential

    https://travail-emploi.gouv.fr/formation-professionnelle/acteurs-cadre-et-qualite-de-la-formation-professionnelle/article/qualiopi-marque-de-certification-qualite-des-prestataires-de-formation
    """

    __tablename__ = "base_sale_product_qualiopi"
    __table_args__ = default_table_args
    # When we will reach SQLA≥2 ; use polymorphic_abstract: True instead of polymorphic_identity
    __mapper_args__ = {"polymorphic_identity": "base_sale_product_qualiopi"}

    __duplicable_fields__ = SaleProductWork.__duplicable_fields__ + [
        "access_delay",
        "accessibility",
        "content",
        "duration_hours",
        "group_size",
        "presence_modality",
        # "results",  # Not relevant in case of copy
        "teaching_method",
        "trainer",
    ]

    __injectable_fields__ = [
        # BaseSaleProduct
        "label",
        "description",
        "ref",
        # SaleProductWork
        "title",
        # BaseQualiopiSaleProduct
        "access_delay",
        "accessibility",
        "content",
        "duration_hours",
        "group_size_label",
        "presence_modality_label",
        "teaching_method",
        "trainer",
        "results",
    ]

    id = Column(
        Integer,
        ForeignKey("sale_product_work.id", ondelete="cascade"),
        primary_key=True,
    )

    accessibility = Column(
        Text,
        info={
            "colanderalchemy": {
                "title": "Accessibilité aux personnes handicapées",
                "description": (
                    "Accessibilité et politique d’accueil des personnes en "
                    "situation de handicap"
                ),
            }
        },
        nullable=False,
        default="",
    )
    duration_hours = Column(
        Float,
        info={
            "colanderalchemy": {
                "title": "Durée totale, en heures",
            }
        },
        nullable=True,
    )

    presence_modality = Column(
        String(20),
        info={
            "colanderalchemy": {
                "title": "Modalité de présence",
                "validator": colander.OneOf([i[0] for i in PRESENCE_MODALITY_OPTIONS]),
            }
        },
        nullable=False,
        default="physical",
    )

    @property
    def presence_modality_label(self):
        return PRESENCE_MODALITY_MAP.get(self.presence_modality, "")

    group_size = Column(
        String(20),
        info={
            "colanderalchemy": {
                "title": "Groupe / individuel",
                "validator": colander.OneOf([i[0] for i in GROUP_SIZES_OPTIONS]),
            }
        },
        default="group",
    )

    @property
    def group_size_label(self):
        return GROUP_SIZES_MAP.get(self.group_size, "")

    content = Column(
        Text,
        info={
            "colanderalchemy": {
                "title": "Contenu détaillé de la formation",
                "description": "Trame par étapes, programme…",
            }
        },
        nullable=False,
        default="",
    )
    teaching_method = Column(
        Text,
        info={
            "colanderalchemy": {"title": "Moyens pédagogiques et méthodes utilisées"}
        },
        nullable=False,
        default="",
    )
    results = Column(
        Text,
        info={
            "colanderalchemy": {
                "title": "Résultats",
                "description": "Taux de réussite, taux de satisfaction, données vérifiables, Taux d’obtention de certification.",
            }
        },
        nullable=False,
        default="",
    )
    trainer = Column(
        Text,
        info={
            "colanderalchemy": {
                "title": "Intervenant·e",
            }
        },
        nullable=False,
        default="",
    )
    access_delay = Column(
        Text,
        info={
            "colanderalchemy": {
                "title": "Délai d'accès",
                "description": "Durée estimée entre la demande du bénéficiaire et le début de la prestation",
            }
        },
        nullable=False,
        default="",
    )

    def __json__(self, request):
        result = super().__json__(request)
        result.update(
            accessibility=self.accessibility,
            access_delay=self.access_delay,
            content=self.content,
            duration_hours=self.duration_hours,
            group_size=self.group_size,
            presence_modality=self.presence_modality,
            results=self.results,
            teaching_method=self.teaching_method,
            trainer=self.trainer,
        )
        return result


class BaseQualiopiKnowledgeSaleProduct(BaseQualiopiSaleProduct):
    """
    Common base for VAE / Training

    (no business logic except they share several fields)
    """

    __tablename__ = "base_sale_product_qualiopi_knowledge"
    __table_args__ = default_table_args
    __mapper_args__ = {
        # When we will reach SQLA≥2 ; use polymorphic_abstact: True instead of polymorphic_identity
        "polymorphic_identity": "base_sale_product_qualiopi_knowledge",
    }
    __duplicable_fields__ = BaseQualiopiSaleProduct.__duplicable_fields__ + [
        "goals",
        "for_who",
        "duration_days",
        "evaluation",
        "place",
    ]
    __injectable_fields__ = BaseQualiopiSaleProduct.__injectable_fields__ + [
        "goals",
        "for_who",
        "duration_days",
        "evaluation",
        "place",
    ]

    id = Column(
        Integer,
        ForeignKey("base_sale_product_qualiopi.id", ondelete="cascade"),
        primary_key=True,
    )
    goals = Column(
        Text,
        info={
            "colanderalchemy": {
                "title": "Objectifs à atteindre à l'issue de la formation",
                "description": (
                    "Les objectifs doivent être obligatoirement décrits avec des"
                    " verbes d'actions."
                ),
            }
        },
        nullable=False,
        default="",
    )
    for_who = Column(
        Text,
        info={
            "colanderalchemy": {
                "title": "Public cible",
                "description": "À qui s'adresse la formation.",
            }
        },
        nullable=False,
        default="",
    )
    duration_days = Column(
        Float,
        info={
            "colanderalchemy": {
                "title": "Nombre de jours",
            }
        },
        nullable=True,
    )
    evaluation = Column(
        Text,
        info={
            "colanderalchemy": {
                "title": "Modalités d'évaluation de la formation",
                "description": (
                    "Par exemple : questionnaire d'évaluation, exercices-tests,"
                    " questionnaire de satisfaction, évaluation formative."
                ),
            }
        },
        nullable=False,
        default="",
    )
    place = Column(
        Text,
        info={
            "colanderalchemy": {
                "title": "Lieu de la formation",
                "description": (
                    "Villes, zones géographiques où la formation peut être mise en "
                    "place."
                ),
            }
        },
        nullable=False,
        default="",
    )

    def __json__(self, request):
        result = super().__json__(request)
        result.update(
            goals=self.goals,
            for_who=self.for_who,
            duration_days=self.duration_days,
            evaluation=self.evaluation,
            place=self.place,
        )
        return result


class SaleProductTraining(BaseQualiopiKnowledgeSaleProduct):
    __tablename__ = "sale_product_training"
    __table_args__ = default_table_args
    __mapper_args__ = {"polymorphic_identity": "sale_product_training"}

    __duplicable_fields__ = BaseQualiopiKnowledgeSaleProduct.__duplicable_fields__ + [
        "rncp_rs_code",
        "certification_date",
        "certification_name",
        "certificator_name",
        "gateways",
        "modality_one",
        "modality_two",
        "prerequisites",
    ]

    __injectable_fields__ = BaseQualiopiKnowledgeSaleProduct.__injectable_fields__ + [
        "mixing_modality_label",
        "rncp_rs_code",
        "certification_date",
        "certification_name",
        "certificator_name",
        "gateways",
        "prerequisites",
    ]

    _caerp_service = SaleProductTrainingService

    id = Column(
        Integer,
        ForeignKey("base_sale_product_qualiopi_knowledge.id", ondelete="cascade"),
        primary_key=True,
    )
    rncp_rs_code = Column(
        String(20),
        info={
            "colanderalchemy": {
                "title": "Code RNCP/RS",
                "description": "Si formation certifiante uniquement, de forme RNCPXXXXX ou RSXXXX.",
                "validator": validate_rncp_rs_code,
            }
        },
        default="",
        nullable=False,
    )
    certification_name = Column(
        String(100),
        info={
            "colanderalchemy": {
                "title": "Libellé de la certification",
                "description": "Si formation certifiante uniquement.",
            }
        },
        default="",
        nullable=False,
    )
    certificator_name = Column(
        String(50),
        info={
            "colanderalchemy": {
                "title": "Nom du certificateur",
                "description": "Si formation certifiante uniquement.",
            }
        },
        nullable=True,
    )
    certification_date = Column(
        Date(),
        info={
            "colanderalchemy": {
                "title": "Date de la certification",
                "description": "Si formation certifiante uniquement.",
            }
        },
        nullable=True,
    )
    gateways = Column(
        Text,
        info={
            "colanderalchemy": {
                "title": "Passerelles et débouchés",
                "description": "Si formation certifiante uniquement.",
            }
        },
        default="",
        nullable=False,
    )
    prerequisites = Column(
        Text,
        info={"colanderalchemy": {"title": "Pré-requis obligatoire de la formation"}},
        nullable=False,
        default="",
    )
    modality_one = Column(
        Boolean(),
        info={"colanderalchemy": {"title": "Formation intra-entreprise"}},
        default=False,
    )
    modality_two = Column(
        Boolean(),
        info=({"colanderalchemy": {"title": "Formation inter-entreprise"}}),
        default=False,
    )

    @property
    def mixing_modality_label(self):
        if self.modality_one and self.modality_two:
            return "Inter ou Intra-entreprise"
        elif self.modality_one:
            return "Intra-entreprise"
        elif self.modality_two:
            return "Inter-Entreprise"
        else:
            return "Inter/Intra inconnu"

    def __json__(self, request):
        """
        Json repr of our model
        """
        result = super().__json__(request)
        result.update(
            certification_date=self.certification_date,
            certification_name=self.certification_name,
            certificator_name=self.certificator_name,
            gateways=self.gateways,
            modality_one=self.modality_one,
            modality_two=self.modality_two,
            prerequisites=self.prerequisites,
            rncp_rs_code=self.rncp_rs_code,
        )
        return result


class SaleProductVAE(BaseQualiopiKnowledgeSaleProduct):
    __tablename__ = "sale_product_vae"
    __table_args__ = default_table_args
    __mapper_args__ = {"polymorphic_identity": "sale_product_vae"}

    __duplicable_fields__ = BaseQualiopiKnowledgeSaleProduct.__duplicable_fields__ + [
        "eligibility_process",
    ]

    __injectable_fields__ = BaseQualiopiKnowledgeSaleProduct.__injectable_fields__ + [
        "eligibility_process",
    ]

    _caerp_service = SaleProductVAEService

    id = Column(
        Integer,
        ForeignKey("base_sale_product_qualiopi_knowledge.id", ondelete="cascade"),
        primary_key=True,
    )
    eligibility_process = Column(
        Text,
        info={
            "colanderalchemy": {"title": "Processus d’éligibilité et de recevabilité"}
        },
        nullable=False,
        default="",
    )

    def __json__(self, request):
        result = super().__json__(request)
        result.update(
            eligibility_process=self.eligibility_process,
        )
        return result

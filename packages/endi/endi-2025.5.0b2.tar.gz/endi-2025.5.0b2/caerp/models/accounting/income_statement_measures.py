import logging
import datetime

from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    Date,
)

from caerp_base.models.base import (
    default_table_args,
)
from caerp.models.accounting.base import (
    BaseAccountingMeasureTypeCategory,
    BaseAccountingMeasureType,
    BaseAccountingMeasureGrid,
    BaseAccountingMeasure,
)
from caerp.models.accounting.services import (
    IncomeStatementMeasureGridService,
)


logger = logging.getLogger(__name__)


class IncomeStatementMeasureTypeCategory(BaseAccountingMeasureTypeCategory):
    """
    Categories joining different IncomeStatementMeasureTypes
    """

    __tablename__ = "income_statement_measure_type_category"
    __table_args__ = default_table_args
    __mapper_args__ = {"polymorphic_identity": "income_statement"}
    __colanderalchemy_config__ = {
        "help_msg": """Les catégories permettent de regrouper les types
        d'indicateurs afin d'en faciliter la configuration.
        Ils peuvent ensuite être utilisé pour calculer des totaux.<br />
        """
    }
    id = Column(
        ForeignKey(
            "base_accounting_measure_type_category.id",
            ondelete="CASCADE",
        ),
        primary_key=True,
        info={"colanderalchemy": {"exclude": True}},
    )


class IncomeStatementMeasureType(BaseAccountingMeasureType):
    """
    IncomeStatement measure type
    """

    __tablename__ = "income_statement_measure_type"
    __table_args__ = default_table_args
    __mapper_args__ = {"polymorphic_identity": "income_statement"}
    __colanderalchemy_config__ = {
        "help_msg": """Les indicateurs de comptes résultats permettent de
        regrouper des écritures sous un même libellé.<br />
        Ils permettent d'assembler les comptes de résultats des entrepreneurs.
        <br />Vous pouvez définir ici les préfixes de comptes généraux pour
        indiquer quelles écritures doivent être utilisées pour calculer cet
        indicateur.
        <br />
        Si nécessaire vous pourrez alors recalculer les derniers indicateurs
        générés.
        """
    }
    id = Column(
        ForeignKey(
            "base_accounting_measure_type.id",
            ondelete="CASCADE",
        ),
        primary_key=True,
        info={"colanderalchemy": {"exclude": True}},
    )

    @staticmethod
    def default_sign():
        return -1


class IncomeStatementMeasureGrid(BaseAccountingMeasureGrid):
    """
    A grid of measures, one grid per month/year couple

    """

    __tablename__ = "income_statement_measure_grid"
    __table_args__ = default_table_args
    __mapper_args__ = {"polymorphic_identity": "income_statement"}

    id = Column(
        ForeignKey(
            "base_accounting_measure_grid.id",
            ondelete="CASCADE",
        ),
        primary_key=True,
        info={"colanderalchemy": {"exclude": True}},
    )
    month = Column(Integer, info={"colanderalchemy": {"title": "Mois"}})
    year = Column(Integer, info={"colanderalchemy": {"title": "Année"}})
    updated_at = Column(
        Date(),
        info={
            "colanderalchemy": {
                "exclude": True,
                "title": "Mis à jour le",
            }
        },
        default=datetime.date.today,
        onupdate=datetime.date.today,
        nullable=False,
    )
    _caerp_service = IncomeStatementMeasureGridService


class IncomeStatementMeasure(BaseAccountingMeasure):
    """
    Stores a income_statement measure associated to a given company
    """

    __tablename__ = "income_statement_measure"
    __table_args__ = default_table_args
    __mapper_args__ = {"polymorphic_identity": "income_statement"}
    id = Column(
        ForeignKey(
            "base_accounting_measure.id",
            ondelete="CASCADE",
        ),
        primary_key=True,
        info={"colanderalchemy": {"exclude": True}},
    )

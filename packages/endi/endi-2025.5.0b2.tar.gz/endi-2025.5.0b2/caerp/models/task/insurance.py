"""
Modèle pour les assurances dans les devis et factures
"""
import sqlalchemy as sa

from caerp_base.models.base import DBSESSION
from caerp.models.options import (
    ConfigurableOption,
    get_id_foreignkey_col,
)


class TaskInsuranceOption(ConfigurableOption):
    """
    Insurance options
    """

    __colanderalchemy_config__ = {
        "title": "Taux d'assurance des devis/factures",
        "description": (
            "Configurer les taux d'assurance et leurs mentions spécifiques"
        ),
    }
    id = get_id_foreignkey_col("configurable_option.id")
    rate = sa.Column(
        sa.Numeric(4, 2, asdecimal=False),
        info={"colanderalchemy": {"title": "Taux (en %)"}},
        nullable=False,
        default=0,
    )
    title = sa.Column(
        sa.String(255),
        default="",
        info={
            "colanderalchemy": {
                "title": "Titre à afficher dans les PDF",
                "description": (
                    "Texte apparaissant sous forme de titre dans la sortie PDF"
                    " (facultatif)"
                ),
            }
        },
    )
    full_text = sa.Column(
        sa.Text(),
        info={
            "colanderalchemy": {
                "title": "Texte à afficher dans les PDF",
                "description": (
                    "Si ce taux d'assurance a été affecté à un devis/facture,"
                    " ce texte apparaitra dans la sortie PDF"
                ),
            }
        },
    )

    def __json__(self, request):
        dic = super(TaskInsuranceOption, self).__json__(request)
        dic.update(
            dict(
                rate=self.rate,
            )
        )
        return dic

    @property
    def is_used(self):
        from caerp.models.task import Task

        return (
            DBSESSION().query(Task.id).filter(Task.insurance_id == self.id).count() > 0
        )

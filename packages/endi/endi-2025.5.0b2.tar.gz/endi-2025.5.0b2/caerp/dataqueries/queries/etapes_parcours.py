import logging

from caerp_base.models.base import DBSESSION

from caerp.dataqueries.base import BaseDataQuery
from caerp.models.career_path import PERIOD_OPTIONS, CareerPath
from caerp.models.career_stage import STAGE_TYPE_OPTIONS
from caerp.models.user.utils import (
    get_ongoing_parcours,
    get_tuple_option_label,
    get_user_analytical_accounts,
)
from caerp.utils.dataqueries import dataquery_class

logger = logging.getLogger(__name__)


@dataquery_class()
class CareerPathQuery(BaseDataQuery):

    name = "etapes_parcours"
    label = "Liste des étapes de parcours sur une période"
    description = """
    Liste de toutes les étapes de parcours réalisées sur la période choisie.
    """

    def default_dates(self):
        self.start_date = self.date_tools.year_start()
        self.end_date = self.date_tools.year_end()

    def headers(self):
        headers = [
            "ID Utilisateur",
            "Code(s) analytique(s)",
            "Civilité",
            "Nom",
            "Prénom",
            "Antenne de rattachement",
            "Typologie d'activité",
            "Date d'entrée dans la CAE",
            "Étape",
            "Nature",
            "Nouvelle situation",
            "Date d'effet",
            "Date d'échéance",
            "CONTRATS",
            "Type de contrat",
            "Qualité du salarié",
            "Taux horaire",
            "Nombre d'heures",
            "Salaire brut",
            "Objectif de CA / d'activité",
            "Numéro d'avenant",
            "SORTIES",
            "Type de sortie",
            "Motif de sortie",
        ]
        return headers

    def data(self):
        data = []
        steps = (
            DBSESSION()
            .query(CareerPath)
            .filter(CareerPath.start_date.between(self.start_date, self.end_date))
            .order_by(CareerPath.start_date)
            .all()
        )
        for s in steps:
            if not s.userdatas:
                logger.warning(f"Career path without userdatas (id={s.id})")
                continue
            parcours = get_ongoing_parcours(s.userdatas.id, at_date=self.end_date)
            stage_type_label = ""
            if s.career_stage:
                stage_type_label = get_tuple_option_label(
                    STAGE_TYPE_OPTIONS, s.career_stage.stage_type
                )
            goals_amount_str = ""
            if s.goals_amount:
                goals_amount_str = "{} {}".format(
                    s.goals_amount,
                    get_tuple_option_label(PERIOD_OPTIONS, s.goals_period),
                )
            u = s.userdatas
            contract_data = [
                u.user_id,
                get_user_analytical_accounts(u.user_id),
                u.coordonnees_civilite,
                u.coordonnees_lastname,
                u.coordonnees_firstname,
                u.situation_antenne.label if u.situation_antenne else "",
                u.activity_typologie.label if u.activity_typologie else "",
                self.date_tools.format_date(parcours.entry_date if parcours else None),
                s.career_stage.name if s.career_stage else "",
                stage_type_label,
                s.cae_situation.label if s.cae_situation else "",
                self.date_tools.format_date(s.start_date),
                self.date_tools.format_date(s.end_date),
                "",
                s.type_contrat.label if s.type_contrat else "",
                s.employee_quality.label if s.employee_quality else "",
                s.taux_horaire,
                s.num_hours,
                s.parcours_salary,
                goals_amount_str,
                s.amendment_number,
                "",
                s.type_sortie.label if s.type_sortie else "",
                s.motif_sortie.label if s.motif_sortie else "",
            ]
            data.append(contract_data)
        return data

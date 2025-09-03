import datetime
import logging

from dateutil.relativedelta import relativedelta

from caerp.models.user.utils import (
    get_all_userdatas_active_on_period,
    get_userdatas_seniority,
    get_user_analytical_accounts,
    get_social_statuses_label,
    get_userdatas_cae_situation,
    get_user_companies_names,
    get_user_companies_goals,
    get_user_companies_activities,
    get_user_turnover,
    get_ongoing_parcours,
)
from caerp.dataqueries.base import BaseDataQuery
from caerp.utils.dataqueries import dataquery_class
from caerp.utils.strings import short_month_name


logger = logging.getLogger(__name__)


@dataquery_class()
class ESTurnoversQuery(BaseDataQuery):
    name = "ca_porteurs_periode"
    label = "Chiffre d'affaire par entrepreneur"
    description = """
    <p>Chiffre d'affaire (total et mensuel) par entrepreneur actif sur la période 
    choisie avec des informations utiles pour les statistiques.</p>
    <br/>
    <p><strong>NB</strong> : Pour les enseignes multi-porteurs le CA sera réparti 
    équitablement entre chaque entrepreneur actif.</p>
    <br/>
    <p><em>Exemples :<ul>
    <li>CA homme / femme</li>
    <li>CA par statut d’entrepreneur (CAPE, CESA, associés)</li>
    <li>CA par typologie de métier</li>
    <li>Etc...</li>
    </ul></em></p>
    """

    def default_dates(self):
        self.start_date = self.date_tools.year_start()
        self.end_date = self.date_tools.year_end()

    def headers(self):
        headers = [
            "ID Utilisateur",
            "Identifiant interne",
            "Code(s) analytique(s)",
            "Civilité",
            "Nom",
            "Prénom",
            "Sexe",
            "Age",
            "Code postal",
            "Ville",
            "Zone d'habitation",
            "Qualification de la zone d'habitation",
            "Statut social à l'entrée",
            "Statut social actuel",
            "Antenne de rattachement",
            "Situation actuelle dans la CAE",
            "Date d'entrée dans la CAE",
            "Ancienneté (en mois)",
            "Date de contrat",
            "Date d'entrée au sociétariat",
            "Date de sortie",
            "Motif de sortie",
            "-----",
            "Typologie d'activité",
            "Enseigne(s)",
            "Descriptif(s) d'activité(s)",
            "Domaine d’activité principal",
            "-----",
            "CA TOTAL",
        ]
        months = self.date_tools.get_period_months(self.start_date, self.end_date)
        for (year, month) in months:
            headers.append(f"CA {short_month_name(month)} {str(year)[2:]}")
        return headers

    def data(self):
        data = []
        active_users = get_all_userdatas_active_on_period(
            self.start_date, self.end_date
        )
        for u in active_users:
            parcours = get_ongoing_parcours(u.id, self.end_date)

            if parcours is None:
                logger.warning(
                    f"Missing CareerPath of type entry/contract for Userdatas {u.id}"
                )
                seniority = 0
                entry_date = None
                contract_date = None
            else:
                seniority = get_userdatas_seniority(u.id, at_date=datetime.date.today())
                entry_date = parcours.entry_date
                contract_date = parcours.contract_date

            cae_situation = get_userdatas_cae_situation(u.id, self.end_date)
            user_data = [
                u.user_id,
                u.coordonnees_identifiant_interne,
                get_user_analytical_accounts(u.user_id),
                u.coordonnees_civilite,
                u.coordonnees_lastname,
                u.coordonnees_firstname,
                u.coordonnees_sex,
                self.date_tools.age(u.coordonnees_birthday, self.end_date),
                u.coordonnees_zipcode,
                u.coordonnees_city,
                u.coordonnees_zone.label if u.coordonnees_zone else "",
                u.coordonnees_zone_qual.label if u.coordonnees_zone_qual else "",
                get_social_statuses_label(u.social_statuses),
                get_social_statuses_label(u.today_social_statuses),
                u.situation_antenne.label if u.situation_antenne else "",
                cae_situation.label if cae_situation else "",
                self.date_tools.format_date(entry_date),
                seniority,
                self.date_tools.format_date(contract_date),
                self.date_tools.format_date(u.situation_societariat_entrance),
            ]
            if parcours and parcours.exit:
                user_data += [
                    self.date_tools.format_date(parcours.exit.start_date),
                    parcours.exit.motif_sortie.label
                    if parcours.exit.motif_sortie
                    else "",
                ]
            else:
                user_data += [
                    "",
                    "",
                ]
            user_data += [
                "",
                u.activity_typologie.label if u.activity_typologie else "",
                get_user_companies_names(u.user_id),
                get_user_companies_goals(u.user_id),
                get_user_companies_activities(u.user_id, only_main=True),
                "",
                get_user_turnover(u.user_id, self.start_date, self.end_date),
            ]
            months = self.date_tools.get_period_months(self.start_date, self.end_date)
            for (year, month) in months:
                month_start = datetime.date(year, month, 1)
                month_end = (
                    month_start + relativedelta(months=1) - relativedelta(days=1)
                )
                user_data.append(get_user_turnover(u.user_id, month_start, month_end))
            data.append(user_data)
        return data

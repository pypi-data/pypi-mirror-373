import logging

from caerp.dataqueries.base import BaseDataQuery
from caerp.models.user.utils import (
    get_all_userdatas_active_on_period,
    get_active_custom_fields,
    get_custom_field_value_string,
)
from caerp.utils.dataqueries import dataquery_class


logger = logging.getLogger(__name__)


@dataquery_class()
class LieuProductionQuery(BaseDataQuery):
    name = "lieux_de_production"
    label = "[AGRI] Lieux de production liés à des porteurs actifs sur une période"
    description = """
    <p>Liste de tous les lieux de productions liés à des porteurs de projets 
    actifs sur la période choisie.</p>
    <br/>
    <p>Un porteur de projet est considéré comme actif si :<ul>
    <li>sa date d'entrée <em>(date de la première étape de parcours de type 
    "Entrée CAE", généralement un CAPE)</em> est avant la fin de la période</li>
    <li>sa date de sortie <em>(date de la dernière étape de parcours de type 
    "Sortie CAE")</em> n'existe pas ou est après le début de la période</li>
    </ul></p>
    <br/>
    <p><strong>Le champ complémentaire agricole "Lieu de production" doit être activé
    pour pouvoir éxécuter cette requête.</strong></p>
    <p>Les lieux collectifs doivent être libellés exactement de la même manière 
    sur toutes les fiches concernées pour pouvoir être regroupés.</p>
    """

    def default_dates(self):
        self.start_date = self.date_tools.year_start()
        self.end_date = self.date_tools.year_end()

    def headers(self):
        headers = [
            "Lieu de production",
            "Mise à disposition des terres",
            "Nombre de producteurs",
            "Liste des producteurs",
            "Typologie d'activité 1",
            "Typologie d'activité 2",
            "Typologie d'activité 3",
            "Typologie d'activité 4",
            "Typologie d'activité 5",
        ]
        return headers

    def data(self):
        # Check if lieu de production is activated
        found = False
        for field in get_active_custom_fields():
            if field == "agri__lieu_production":
                found = True

        # Return empty set if not activated
        if not found:
            return []

        data = []
        active_users = get_all_userdatas_active_on_period(
            self.start_date, self.end_date
        )
        # Find distinct lieu de production
        lieux = {}
        for u in active_users:
            lieu = u.custom_fields.agri__lieu_production

            if lieu is None:
                continue

            if lieu not in lieux.keys():
                lieux[lieu] = [u]
            else:
                lieux[lieu].append(u)

        for l in lieux:
            # List of producer
            producer_list = ""
            first = True
            for p in lieux[l]:
                if first:
                    producer_list += p.coordonnees_lastname
                    first = False
                else:
                    producer_list += ", " + p.coordonnees_lastname

            # Typologies
            typologie_1 = lieux[l][0].activity_typologie.label
            typologie_2 = ""
            if len(lieux[l]) >= 2:
                typologie_2 = lieux[l][1].activity_typologie.label
            typologie_3 = ""
            if len(lieux[l]) >= 3:
                typologie_3 = lieux[l][2].activity_typologie.label
            typologie_4 = ""
            if len(lieux[l]) >= 4:
                typologie_4 = lieux[l][3].activity_typologie.label
            typologie_5 = ""
            if len(lieux[l]) >= 5:
                typologie_5 = lieux[l][4].activity_typologie.label

            dispo_terres = get_custom_field_value_string(
                lieux[l][0], "agri__dispo_terres"
            )

            lieux_data = [
                l,
                dispo_terres,
                len(lieux[l]),
                producer_list,
                typologie_1,
                typologie_2,
                typologie_3,
                typologie_4,
                typologie_5,
            ]
            data.append(lieux_data)

        return data

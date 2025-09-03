import datetime
from typing import List, Tuple

from colanderalchemy import SQLAlchemySchemaNode
from sqlalchemy import func
from sqlalchemy.orm import aliased

from caerp_base.models.base import DBSESSION
from caerp_base.models.utils import non_null_sum
from caerp.compute.math_utils import integer_to_amount
from caerp.models.project.business import Business
from caerp.models.task import Invoice
from caerp.utils.sys_environment import resource_filename


class BPFSpecInterface:
    @classmethod
    def stream_csv_rows(cls, query):
        """
        :param query Query<BPFData>:
        """
        raise NotImplemented

    @classmethod
    def get_colander_schema(cls, is_subcontract: bool) -> SQLAlchemySchemaNode:
        raise NotImplemented


def collect_categories_ids(categories):
    """
    Collects ids, and return a flat list of ids.

    :param list categories: flat or nested (max 1 level) categories in a
      list
    :yield: int
    """
    for id_, _, subcategories in categories:
        if id_ is None:
            for subcategory_id, _ in subcategories:
                yield subcategory_id
        else:
            yield id_


class Cerfa_10443_14(BPFSpecInterface):
    """
    https://www.formulaires.modernisation.gouv.fr/gf/getNotice.do?cerfaFormulaire=10443&cerfaNotice=50199
    https://www.formulaires.modernisation.gouv.fr/gf/cerfa_10443.do
    """

    ods_template = resource_filename("sample_templates/bpf/CERFA 10443*14.ods")

    INCOME_SOURCES = [
        (0, "Entreprises pour la formation de leurs salariés", []),
        (
            None,
            "Organismes paritaires collecteurs ou gestionnaires des fonds de la"
            " formation",
            [
                (1, "contrats de professionnalisation"),
                (2, "congés individuels de formation"),
                (3, "compte personnel de formation"),
                (
                    4,
                    "autres dispositifs (plan de formation, périodes de"
                    " professionnalisation, …)",
                ),
                (
                    5,
                    "pour des formations dispensées dans le cadre d’autres dispositifs"
                    " (plan de formation, périodes de professionnalisation",
                ),
            ],
        ),
        (6, "Fonds d'assurance", []),
        (
            7,
            "Pouvoirs publics pour la formation de leurs agents (Etat, collectivités"
            " territoriales, établissements publics à caractère administratif)",
            [],
        ),
        (
            None,
            "Pouvoirs publics pour la formation de publics spécifiques",
            [
                (8, "Instances européennes"),
                (9, "État"),
                (10, "Conseils régionaux"),
                (11, "Pôle emploi"),
                (12, "Autres ressources publiques"),
            ],
        ),
        (
            13,
            "Contrats conclus avec des personnes à titre individuel et à leurs frais",
            [],
        ),
        (14, "Contrats conclus avec d’autres organismes de formation", []),
        (15, "Produits résultant de la vente d’outils pédagogiques", []),
        (16, "Autres produits au titre de la formation professionnelle continue", []),
    ]

    TRAINING_GOALS = [
        (
            None,
            "Formations visant un diplôme ou un titre à finalité professionnelle (hors"
            " certificat de qualification professionnelle) inscrit au Répertoire"
            " national des certifications professionnelles (RNCP)",
            [
                (
                    0,
                    "Niveau I et II (licence, maîtrise, master, DEA, DESS, diplôme"
                    " d’ingénieur)",
                ),
                (1, "Niveau III (BTS, DUT, écoles de formation sanitaire et sociale…)"),
                (2, "Niveau III (BTS, DUT, écoles de formation sanitaire et sociale…)"),
                (3, "Niveau IV (BAC professionnel, BT, BP, BM…)"),
            ],
        ),
        (4, "Certificat de qualification professionnelle (CQP)", []),
        (
            5,
            "Certification et/ou une habilitation inscrite à l’inventaire de la CNCP",
            [],
        ),
        (6, "Autres formations professionnelles continues", []),
        (7, "Bilan de compétences", []),
        (8, "Actions d'accompagnement à la validation des acquis d'expérience", []),
    ]

    TRAINEE_TYPES = [
        (
            0,
            "Salariés bénéficiant d’un financement par l’employeur, par un OPCA ou un"
            " OPACIF",
            [],
        ),
        (1, "Personnes en recherche d’emploi bénéficiant d’un financement public", []),
        (2, "Personnes en recherche d’emploi bénéficiant d’un financement OPCA", []),
        (3, "Particuliers à leurs propres frais", []),
        (4, "Autres stagiaires", []),
    ]

    @classmethod
    def get_income_sources_ids(cls):
        return list(collect_categories_ids(cls.INCOME_SOURCES))

    @classmethod
    def get_training_goals_ids(cls):
        return list(collect_categories_ids(cls.TRAINING_GOALS))

    @classmethod
    def get_trainee_types_ids(cls):
        return list(collect_categories_ids(cls.TRAINEE_TYPES))

    @staticmethod
    def _matching_query(bpf_data_query, *args, **kwargs):
        # avoid circular dependency
        from caerp.models.training.bpf import BusinessBPFData

        aliased_bpf_data_query = aliased(
            BusinessBPFData,
            bpf_data_query.subquery(),
        )
        return DBSESSION.query(*args, **kwargs).join(
            aliased_bpf_data_query, aliased_bpf_data_query.id == BusinessBPFData.id
        )

    @classmethod
    def sum_bpf_datas(cls, bpf_data_query):
        from caerp.models.training.bpf import BusinessBPFData

        return cls._matching_query(
            bpf_data_query,
            non_null_sum(BusinessBPFData.has_subcontract_hours).label(
                "has_subcontract_hours"
            ),
            non_null_sum(BusinessBPFData.has_subcontract_headcount).label(
                "has_subcontract_headcount"
            ),
            non_null_sum(BusinessBPFData.remote_headcount).label("remote_headcount"),
        ).first()

    @classmethod
    def _is_subcontract_stats(cls, bpf_data_query, is_subcontract_value):
        from caerp.models.training.bpf import BusinessBPFData

        query = cls._matching_query(
            bpf_data_query,
            non_null_sum(BusinessBPFData.total_hours).label("total_hours"),
            non_null_sum(BusinessBPFData.headcount).label("headcount"),
        ).filter(
            BusinessBPFData.is_subcontract == is_subcontract_value,
        )
        return query.first()

    @classmethod
    def is_subcontract_stats(cls, bpf_data_query):
        """
        Data for « F - 2. ACTIVITÉ EN PROPRE DE L’ORGANISME »

        Gather data for everything that is subcontract

        :returns: info as row attributes : `total_hours` and `headcount`
        :rtype sqlalchemy.engine.RowProxy:
        """
        return cls._is_subcontract_stats(
            bpf_data_query,
            is_subcontract_value=True,
        )

    @classmethod
    def is_not_subcontract_stats(cls, bpf_data_query):
        """
        Data for « F - 2. ACTIVITÉ EN PROPRE DE L’ORGANISME »

        Gather data for everything that is not subcontract

        :returns: info as row attributes : `total_hours` and `headcount`
        :rtype sqlalchemy.engine.RowProxy:
        """
        return cls._is_subcontract_stats(
            bpf_data_query,
            is_subcontract_value=False,
        )

    @classmethod
    def has_subcontract_stats(cls, bpf_data_query):
        """
        Data for « F - 2. ACTIVITÉ EN PROPRE DE L’ORGANISME »

        Gather data for everything that is not subcontract

        :returns: info as row attributes : `total_hours` and `headcount`
        :rtype sqlalchemy.engine.RowProxy:
        """
        return cls._is_subcontract_stats(
            bpf_data_query,
            is_subcontract_value=False,
        )

    @classmethod
    def cost_stats(cls, bpf_data_query):
        """
        Data for « D. BILAN FINANCIER HORS TAXES »

        :returns dict: of floats (keys: total, subcontracted, internal)
        """
        from caerp.models.training.bpf import BusinessBPFData

        q = cls._matching_query(
            bpf_data_query,
            non_null_sum(BusinessBPFData.has_subcontract_amount).label("subcontracted"),
        )
        result = q.first()
        return dict(
            subcontracted=result.subcontracted,
        )

    @classmethod
    def income_stats(cls, bpf_data_query):
        """
        Data for « C. BILAN FINANCIER HORS TAXES »

        :returns sqlalchemy.orm.Query:
        """
        from caerp.models.training.bpf import IncomeSource

        q = (
            DBSESSION.query(
                IncomeSource.income_category_id.label("category_id"),
                non_null_sum(Invoice.ht).label("amount"),
            )
            .join(
                bpf_data_query.subquery(),
            )
            .join(IncomeSource.invoice)
            .group_by(IncomeSource.income_category_id)
        )

        return cls._fill_category_counter(
            q,
            cls.get_income_sources_ids(),
            ["amount"],
            lambda x: integer_to_amount(x, 5),
        )

    @classmethod
    def training_speciality_stats(cls, bpf_data_query):
        """
        Data for « F - 4. SPÉCIALITÉS DE FORMATION »

        :rtype: iterator of dicts
        """
        from caerp.models.training.bpf import NSFTrainingSpecialityOption
        from caerp.models.training.bpf import BusinessBPFData

        q = (
            cls._matching_query(
                bpf_data_query,
                BusinessBPFData.training_speciality_id,
                NSFTrainingSpecialityOption.label,
                non_null_sum(BusinessBPFData.total_hours).label("total_hours"),
                non_null_sum(BusinessBPFData.headcount).label("headcount"),
            )
            .group_by(
                BusinessBPFData.training_speciality_id,
                NSFTrainingSpecialityOption.label,
            )
            .join(
                NSFTrainingSpecialityOption,
            )
        )

        for row in q:
            code, label = row.label.split(" - ", 1)
            yield {
                "label": label,
                "nsf_code": code,
                "total_hours": row.total_hours,
                "headcount": row.headcount,
            }

    @staticmethod
    def _fill_category_counter(data, categories_ids, attrs, transformer=None):
        """Fill a category counters list with given data

        Category list is used to return zeroed counters for categories absents
        from data.

        :param sqlalchemy.orm.Query data: the data (expected `headcount` and
          `total_hours` cols)
        :param categories list: of int
        :param list attrs: the data attrs that will be rendered as dict keys
        :param transformer: a function to transform the values
        :rtype dict of dicts:
        """
        if transformer is None:
            # pass through
            def transformer(x):
                return x

        # Initialize all counters on all categories to zero values
        ret = {i: {a: 0 for a in attrs} for i in categories_ids}
        # Fill only the categories we have data for
        for row in data:
            ret[row.category_id] = {
                attr: transformer(getattr(row, attr)) for attr in attrs
            }
        return ret

    @classmethod
    def trainee_types_stats(cls, bpf_data_query):
        """
        Data for « F - 1. TYPE DE STAGIAIRES DE L’ORGANISME »

        :returns: stats for each type of trainee.
          List indexes match TRAINEE_TYPES order
        :rtype: list of dict like {'headcount': 42, 'total_hours': 12}.
        """
        from caerp.models.training.bpf import (
            TraineeCount,
            BusinessBPFData,
        )

        q = (
            DBSESSION.query(
                TraineeCount.trainee_type_id.label("category_id"),
                non_null_sum(TraineeCount.headcount).label("headcount"),
                non_null_sum(TraineeCount.total_hours).label("total_hours"),
            )
            .join(
                bpf_data_query.subquery(),
            )
            .filter(
                BusinessBPFData.id == TraineeCount.business_bpf_data_id,
            )
            .group_by(
                TraineeCount.trainee_type_id,
            )
            .order_by(
                TraineeCount.trainee_type_id,
            )
        )
        return cls._fill_category_counter(
            q,
            cls.get_trainee_types_ids(),
            ["headcount", "total_hours"],
        )

    @classmethod
    def training_goals_stats(cls, bpf_data_query):
        """
        Data for « F - 3. OBJECTIF GÉNÉRAL DES PRESTATIONS DISPENSÉES »

        :returns: stats for each type of training goal.
          List indexes match TRAINING_GOALS order
        :rtype: list of dict like {'headcount': 42, 'total_hours': 12}.
        """
        from caerp.models.training.bpf import BusinessBPFData

        q = (
            cls._matching_query(
                bpf_data_query,
                BusinessBPFData.training_goal_id.label("category_id"),
                non_null_sum(BusinessBPFData.total_hours).label("total_hours"),
                non_null_sum(BusinessBPFData.headcount).label("headcount"),
            )
            .group_by(
                BusinessBPFData.training_goal_id,
            )
            .order_by(
                BusinessBPFData.training_goal_id,
            )
        )
        return cls._fill_category_counter(
            q,
            cls.get_training_goals_ids(),
            ["total_hours", "headcount"],
        )

    @classmethod
    def build_template_context(cls, bpf_data_query):
        first_bpf_data = bpf_data_query.first()

        metadata_dict = dict(
            cerfa_version=first_bpf_data.cerfa_version,
            export_date=datetime.date.today(),
            financial_year=first_bpf_data.financial_year,
        )
        data_dict = cls.build_data_dict(bpf_data_query)
        ret_dict = {}
        ret_dict.update(metadata_dict)
        ret_dict.update(data_dict)
        return ret_dict

    @classmethod
    def build_data_dict(cls, bpf_data_query):
        sums = cls.sum_bpf_datas(bpf_data_query)
        trainee_types_stats = cls.trainee_types_stats(bpf_data_query)
        training_goals_stats = cls.training_goals_stats(bpf_data_query)
        is_subcontract_stats = cls.is_subcontract_stats(bpf_data_query)
        is_not_subcontract_stats = cls.is_not_subcontract_stats(bpf_data_query)
        income_stats = cls.income_stats(bpf_data_query)
        cost_stats = cls.cost_stats(bpf_data_query)

        default_val = ""
        data_dict = dict(
            c_ligne_1=income_stats[0]["amount"],
            c_ligne_a=income_stats[1]["amount"],
            c_ligne_b=income_stats[2]["amount"],
            c_ligne_c=income_stats[3]["amount"],
            c_ligne_d=income_stats[4]["amount"],
            c_ligne_e=income_stats[5]["amount"],
            c_ligne_3=income_stats[6]["amount"],
            c_ligne_4=income_stats[7]["amount"],
            c_ligne_5=income_stats[8]["amount"],
            c_ligne_6=income_stats[9]["amount"],
            c_ligne_7=income_stats[10]["amount"],
            c_ligne_8=income_stats[11]["amount"],
            c_ligne_9=income_stats[12]["amount"],
            c_ligne_10=income_stats[13]["amount"],
            c_ligne_11=income_stats[14]["amount"],
            c_ligne_12=income_stats[15]["amount"],
            c_ligne_13=income_stats[16]["amount"],
            d_ligne_1=default_val,
            d_ligne_2=default_val,
            d_ligne_3=cost_stats["subcontracted"],
            e_ligne_1=default_val,
            e_ligne_2=default_val,
            f_1_ligne_a_nb=trainee_types_stats[0]["headcount"],
            f_1_ligne_b_nb=trainee_types_stats[1]["headcount"],
            f_1_ligne_c_nb=trainee_types_stats[2]["headcount"],
            f_1_ligne_d_nb=trainee_types_stats[3]["headcount"],
            f_1_ligne_e_nb=trainee_types_stats[4]["headcount"],
            f_1_ligne_a_h=trainee_types_stats[0]["total_hours"],
            f_1_ligne_b_h=trainee_types_stats[1]["total_hours"],
            f_1_ligne_c_h=trainee_types_stats[2]["total_hours"],
            f_1_ligne_d_h=trainee_types_stats[3]["total_hours"],
            f_1_ligne_e_h=trainee_types_stats[4]["total_hours"],
            f_2_ligne_a_nb=is_not_subcontract_stats.headcount,
            f_2_ligne_b_nb=is_subcontract_stats.headcount,
            f_2_ligne_a_c=is_not_subcontract_stats.total_hours,
            f_2_ligne_b_c=is_subcontract_stats.total_hours,
            f_3_ligne_a1_nb=training_goals_stats[0]["headcount"],
            f_3_ligne_a2_nb=training_goals_stats[1]["headcount"],
            f_3_ligne_a3_nb=training_goals_stats[2]["headcount"],
            f_3_ligne_a4_nb=training_goals_stats[3]["headcount"],
            f_3_ligne_b_nb=training_goals_stats[4]["headcount"],
            f_3_ligne_c_nb=training_goals_stats[5]["headcount"],
            f_3_ligne_d_nb=training_goals_stats[6]["headcount"],
            f_3_ligne_e_nb=training_goals_stats[7]["headcount"],
            f_3_ligne_f_nb=training_goals_stats[8]["headcount"],
            f_3_ligne_a1_h=training_goals_stats[0]["total_hours"],
            f_3_ligne_a2_h=training_goals_stats[1]["total_hours"],
            f_3_ligne_a3_h=training_goals_stats[2]["total_hours"],
            f_3_ligne_a4_h=training_goals_stats[3]["total_hours"],
            f_3_ligne_b_h=training_goals_stats[4]["total_hours"],
            f_3_ligne_c_h=training_goals_stats[5]["total_hours"],
            f_3_ligne_d_h=training_goals_stats[6]["total_hours"],
            f_3_ligne_e_h=training_goals_stats[7]["total_hours"],
            f_3_ligne_f_h=training_goals_stats[8]["total_hours"],
            g_ligne_1_nb=sums.has_subcontract_hours,
            g_ligne_1_h=sums.has_subcontract_headcount,
            f_4=cls.training_speciality_stats(bpf_data_query),
        )
        return data_dict

    @classmethod
    def get_colander_schema(cls, is_subcontract: bool):
        # Avoir circular import
        from caerp.forms.training.bpf import get_business_bpf_edit_schema

        return get_business_bpf_edit_schema(
            extra_excludes=["has_remote"], is_subcontract=is_subcontract
        )


class Cerfa_10443_15(Cerfa_10443_14):
    """
    Contains strictly same data/rules as CERFA 10443*14
    """


class Cerfa_10443_16(Cerfa_10443_15):
    """
    https://www.formulaires.modernisation.gouv.fr/gf/getNotice.do?cerfaFormulaire=10443&cerfaNotice=50199
    https://www.formulaires.modernisation.gouv.fr/gf/cerfa_10443.do
    """

    ods_template = resource_filename("sample_templates/bpf/CERFA 10443*16.ods")

    INCOME_SOURCES = [
        (0, "Entreprises pour la formation de leurs salariés", []),
        (
            None,
            "Organismes gestionnaires des fonds de la formation professionnelle pour"
            " des actions dispensées dans le cadre des :",
            [
                (1, "contrats d'apprentissage"),
                (2, "contrats de professionnalisation"),
                (3, "promotion ou reconversion par alternance"),
                (
                    4,
                    "congés individuels de formation et des projets de transition"
                    " professionnelle",
                ),
                (5, "compte personnel de formation"),
                (6, "dispositifs spécifiques pour les personnes en recherche d’emploi"),
                (7, "dispositifs spécifiques pour les travailleurs non-salariés"),
                (8, "plan de développement des compétences ou d’autres dispositifs"),
            ],
        ),
        (
            10,
            "Pouvoirs publics pour la formation de leurs agents (Etat, collectivités"
            " territoriales, établissements publics à caractère administratif)",
            [],
        ),
        (
            None,
            "Pouvoirs publics pour la formation de publics spécifiques",
            [
                (20, "Instances européennes"),
                (21, "État"),
                (22, "Conseils régionaux"),
                (23, "Pôle emploi"),
                (24, "Autres ressources publiques"),
            ],
        ),
        (
            30,
            "Contrats conclus avec des personnes à titre individuel et à leurs frais",
            [],
        ),
        (
            31,
            "Contrats conclus avec d’autres organismes de formation (y compris CFA)",
            [],
        ),
        (32, "Autres produits au titre de la formation professionnelle continue", []),
    ]

    TRAINEE_TYPES = [
        (0, "Salariés d’employeurs privés hors apprentis", []),
        (1, "Apprentis", []),
        (
            2,
            "Personnes en recherche d’emploi formées par votre organisme de formation",
            [],
        ),
        (
            3,
            "Particuliers à leurs propres frais formés par votre organisme de"
            " formation",
            [],
        ),
        (4, "Autres stagiaires", []),
    ]
    TRAINING_GOALS = [
        (
            None,
            "Formations visant un diplôme ou un titre à finalité professionnelle (hors"
            " certificat de qualification professionnelle) inscrit au Répertoire"
            " national des certifications professionnelles (RNCP)",
            [
                (
                    0,
                    "Niveau 6 à 8 (Licence, Master, diplôme d’ingénieur,"
                    " Doctorat…)....",
                ),
                (
                    1,
                    "Niveau 5 (BTS, DUT, écoles de formation sanitaire et sociale …) .",
                ),
                (2, "Niveau 4 (BAC professionnel, BT, BP, BM…)"),
                (3, "Niveau 3 (BEP, CAP…)....."),
                (4, "Niveau 2"),
                (
                    5,
                    "Certificat de qualification professionnelle (CQP) sans niveau de"
                    " qualification",
                ),
            ],
        ),
        (
            10,
            "Formations visant une certification (dont CQP) ou une habilitation"
            " enregistrée au répertoire spécifique (RS)",
            [],
        ),
        (11, "Formations visant un CQP non enregistré au RNCP ou au RS", []),
        (12, "Autres formations professionnelles", []),
        (13, "Bilan de compétences", []),
        (14, "Actions d'accompagnement à la validation des acquis d'expérience", []),
    ]

    @classmethod
    def build_data_dict(cls, bpf_data_query):
        # Avoid circular import
        from caerp.models.training.bpf import BusinessBPFData

        # F is only about non-subcontracts (porté par l'OF)
        bpf_data_query_nosub = bpf_data_query.filter(
            BusinessBPFData.is_subcontract == False,
        )
        sums = cls.sum_bpf_datas(bpf_data_query_nosub)
        trainee_types_stats = cls.trainee_types_stats(bpf_data_query_nosub)
        training_goals_stats = cls.training_goals_stats(bpf_data_query_nosub)
        training_speciality_stats = cls.training_speciality_stats(bpf_data_query_nosub)

        is_subcontract_stats = cls.is_subcontract_stats(bpf_data_query)
        is_not_subcontract_stats = cls.is_not_subcontract_stats(bpf_data_query)
        income_stats = cls.income_stats(bpf_data_query)
        cost_stats = cls.cost_stats(bpf_data_query)

        default_val = ""
        data_dict = dict(
            # C : income_stats
            c_ligne_1=income_stats[0]["amount"],
            c_ligne_a=income_stats[1]["amount"],
            c_ligne_b=income_stats[2]["amount"],
            c_ligne_c=income_stats[3]["amount"],
            c_ligne_d=income_stats[4]["amount"],
            c_ligne_e=income_stats[5]["amount"],
            c_ligne_f=income_stats[6]["amount"],
            c_ligne_g=income_stats[7]["amount"],
            c_ligne_h=income_stats[8]["amount"],
            c_ligne_3=income_stats[10]["amount"],
            c_ligne_4=income_stats[20]["amount"],
            c_ligne_5=income_stats[21]["amount"],
            c_ligne_6=income_stats[22]["amount"],
            c_ligne_7=income_stats[23]["amount"],
            c_ligne_8=income_stats[24]["amount"],
            c_ligne_9=income_stats[30]["amount"],
            c_ligne_10=income_stats[31]["amount"],
            c_ligne_11=income_stats[32]["amount"],
            # D : cost_stats
            d_ligne_1=default_val,
            d_ligne_2=default_val,
            d_ligne_3=cost_stats["subcontracted"],
            # E
            e_ligne_1_h=default_val,
            e_ligne_2_h=default_val,
            e_ligne_1_nb=default_val,
            e_ligne_2_nb=default_val,
            # F : trainee_type_stats / sums / training_goals_stats / training_speciality
            f_1_ligne_a_nb=trainee_types_stats[0]["headcount"],
            f_1_ligne_b_nb=trainee_types_stats[1]["headcount"],
            f_1_ligne_c_nb=trainee_types_stats[2]["headcount"],
            f_1_ligne_d_nb=trainee_types_stats[3]["headcount"],
            f_1_ligne_e_nb=trainee_types_stats[4]["headcount"],
            f_1_ligne_a_h=trainee_types_stats[0]["total_hours"],
            f_1_ligne_b_h=trainee_types_stats[1]["total_hours"],
            f_1_ligne_c_h=trainee_types_stats[2]["total_hours"],
            f_1_ligne_d_h=trainee_types_stats[3]["total_hours"],
            f_1_ligne_e_h=trainee_types_stats[4]["total_hours"],
            f_1_ligne_1bis_nb=sums.remote_headcount,
            f_2_ligne_2_nb=sums.has_subcontract_headcount,
            f_2_ligne_2_c=sums.has_subcontract_hours,
            f_3_ligne_a1_nb=training_goals_stats[0]["headcount"],
            f_3_ligne_a2_nb=training_goals_stats[1]["headcount"],
            f_3_ligne_a3_nb=training_goals_stats[2]["headcount"],
            f_3_ligne_a4_nb=training_goals_stats[3]["headcount"],
            f_3_ligne_a5_nb=training_goals_stats[4]["headcount"],
            f_3_ligne_a6_nb=training_goals_stats[5]["headcount"],
            f_3_ligne_b_nb=training_goals_stats[10]["headcount"],
            f_3_ligne_c_nb=training_goals_stats[11]["headcount"],
            f_3_ligne_d_nb=training_goals_stats[12]["headcount"],
            f_3_ligne_e_nb=training_goals_stats[13]["headcount"],
            f_3_ligne_f_nb=training_goals_stats[14]["headcount"],
            f_3_ligne_a1_h=training_goals_stats[0]["total_hours"],
            f_3_ligne_a2_h=training_goals_stats[1]["total_hours"],
            f_3_ligne_a3_h=training_goals_stats[2]["total_hours"],
            f_3_ligne_a4_h=training_goals_stats[3]["total_hours"],
            f_3_ligne_a5_h=training_goals_stats[4]["total_hours"],
            f_3_ligne_a6_h=training_goals_stats[5]["total_hours"],
            f_3_ligne_b_h=training_goals_stats[10]["total_hours"],
            f_3_ligne_c_h=training_goals_stats[11]["total_hours"],
            f_3_ligne_d_h=training_goals_stats[12]["total_hours"],
            f_3_ligne_e_h=training_goals_stats[13]["total_hours"],
            f_3_ligne_f_h=training_goals_stats[14]["total_hours"],
            f_4=training_speciality_stats,
            # G : is_subcontract_stats
            g_ligne_1_nb=is_subcontract_stats.headcount,
            g_ligne_1_h=is_subcontract_stats.total_hours,
        )
        return data_dict


class Cerfa_10443_17(Cerfa_10443_16):
    """
    Les modifications comparé au 10443*16 sont minimes :
    - 3 libellés
    - Retrait de la case f_1_ligne_1bis_nb (nb de stagiaires ayant suivi du remote)
    - Ajout du b_ligne_2 (existence de formations remote OUI/NON)
    """

    ods_template = resource_filename("sample_templates/bpf/CERFA 10443*17.ods")

    INCOME_SOURCES = [
        (0, "Entreprises pour la formation de leurs salariés", []),
        (
            None,
            "Organismes gestionnaires des fonds de la formation professionnelle pour"
            " des actions dispensées dans le cadre des :",
            [
                (1, "contrats d'apprentissage"),
                (2, "contrats de professionnalisation"),
                (3, "promotion ou reconversion par alternance"),
                (4, "projets de transition professionnelle"),  # Changé avec 10443*17
                (5, "compte personnel de formation"),
                (6, "dispositifs spécifiques pour les personnes en recherche d’emploi"),
                (7, "dispositifs spécifiques pour les travailleurs non-salariés"),
                (8, "plan de développement des compétences ou d’autres dispositifs"),
            ],
        ),
        (
            10,
            "Pouvoirs publics pour la formation de leurs agents (Etat, collectivités"
            " territoriales, établissements publics à caractère administratif)",
            [],
        ),
        (
            None,
            "Pouvoirs publics pour la formation de publics spécifiques",
            [
                (20, "Instances européennes"),
                (21, "État"),
                (22, "Conseils régionaux"),
                (23, "France travail (ex Pôle emploi)"),  # Changé avec 10443*17
                (24, "Autres ressources publiques"),
            ],
        ),
        (
            30,
            "Contrats conclus avec des personnes à titre individuel et à leurs frais",
            [],
        ),
        (
            31,
            "Contrats conclus avec d’autres organismes de formation (y compris CFA)",
            [],
        ),
        (32, "Autres produits au titre de la formation professionnelle continue", []),
    ]

    TRAINING_GOALS = [
        (
            None,
            "Formations visant un diplôme, un titre à finalité professionnelle ou un"
            " certificat de qualification professionnelle enregistré au Répertoire "
            "national des certifications professionnelles (RNCP)",  # Changé 10443*17
            [
                (
                    0,
                    "Niveau 6 à 8 (Licence, Master, diplôme d’ingénieur,"
                    " Doctorat…)....",
                ),
                (
                    1,
                    "Niveau 5 (BTS, DUT, écoles de formation sanitaire et sociale …) .",
                ),
                (2, "Niveau 4 (BAC professionnel, BT, BP, BM…)"),
                (3, "Niveau 3 (BEP, CAP…)....."),
                (4, "Niveau 2"),
                (
                    5,
                    "Certificat de qualification professionnelle (CQP) sans niveau de"
                    " qualification",
                ),
            ],
        ),
        (
            10,
            "Formations visant une certification (dont CQP) ou une habilitation"
            " enregistrée au répertoire spécifique (RS)",
            [],
        ),
        (11, "Formations visant un CQP non enregistré au RNCP ou au RS", []),
        (12, "Autres formations professionnelles", []),
        (13, "Bilan de compétences", []),
        (14, "Actions d'accompagnement à la validation des acquis d'expérience", []),
    ]

    @classmethod
    def build_data_dict(cls, bpf_data_query):
        from caerp.models.training import BusinessBPFData

        ret = super().build_data_dict(bpf_data_query)
        del ret["f_1_ligne_1bis_nb"]

        # B. Informations générales
        with_remote_query = bpf_data_query.filter(
            BusinessBPFData.has_remote == True
        )  # noqa
        if with_remote_query.count() > 0:
            ret["b_ligne_2"] = "OUI"
        else:
            ret["b_ligne_2"] = "NON"

        return ret

    @classmethod
    def get_colander_schema(cls, is_subcontract: bool):
        # Avoir circular import
        from caerp.forms.training.bpf import get_business_bpf_edit_schema

        return get_business_bpf_edit_schema(
            extra_excludes=["remote_headcount"], is_subcontract=is_subcontract
        )


class BPFService:
    """Handle BPF initialization according to current law"""

    CERFA_VERSIONS = {
        "10443*14": Cerfa_10443_14,
        "10443*15": Cerfa_10443_15,
        "10443*16": Cerfa_10443_16,
        "10443*17": Cerfa_10443_17,
    }

    @classmethod
    def get_spec_from_year(cls, year):
        spec_name = cls.get_spec_name_from_year(year)
        return cls.CERFA_VERSIONS[spec_name]

    @classmethod
    def get_spec_name_from_year(cls, year):
        # If several specs : differentiate on BPF fiscal year
        if year < 2019:
            return "10443*14"
        elif year < 2020:
            return "10443*15"
        elif year < 2023:
            return "10443*16"
        else:
            return "10443*17"

    def _get_field_class(cls, key):
        return cls.FIELD_CLASSES[key]

    @classmethod
    def get_or_create(cls, business_id, financial_year):
        existing = cls.get(
            business_id=business_id,
            financial_year=financial_year,
        )
        if existing is not None:
            return existing
        else:
            return cls.gen_bpf(Business.get(business_id), financial_year)

    @classmethod
    def get(cls, business_id, financial_year):
        # Avoid circular import
        from caerp.models.training.bpf import BusinessBPFData

        query = BusinessBPFData.query().filter_by(
            business_id=business_id,
            financial_year=financial_year,
        )
        if DBSESSION.query(query.exists()).scalar():
            return query.first()
        else:
            return None

    @classmethod
    def gen_bpf(cls, business, financial_year):
        # For now, there is only one cerfa supported In future, we might want
        # to return a different cerfa based on year.
        from caerp.models.training.bpf import BusinessBPFData

        spec_name = cls.get_spec_name_from_year(financial_year)
        return BusinessBPFData(
            business=business,
            cerfa_version=spec_name,
            financial_year=financial_year,
        )

    @classmethod
    def check_businesses_missing_bpf(cls, query, financial_year):
        from caerp.models.training.bpf import BusinessBPFData

        query_missing_bpf = query.filter(
            ~Business.bpf_datas.any(BusinessBPFData.financial_year == financial_year)
        )
        return query_missing_bpf.all()

    @classmethod
    def check_businesses_reused_invoices(
        cls, query, financial_year
    ) -> List[Tuple["Invoice", List["BusinessBPFData"]]]:
        """
        Detects the invoices that are used in several BPFData (through IncomeSource)

        :param query:
        :param financial_year:
        :return: The invoices with multi-use, with the invoice, and for each all the BusinessBPFData related to it
        """
        from caerp.models.training.bpf import BusinessBPFData, IncomeSource

        invoice_use_count = func.count(IncomeSource.invoice_id)

        reused_invoices = (
            (
                query.join(
                    Business.bpf_datas,
                    BusinessBPFData.income_sources,
                    IncomeSource.invoice,
                ).group_by(IncomeSource.invoice_id)
            )
            .with_entities(Invoice, invoice_use_count)
            .having(invoice_use_count > 1)
            .with_entities(Invoice)
        )

        reused_invoices_w_bpfdata = []
        for invoice in reused_invoices:
            q = (
                BusinessBPFData.query()
                .join(IncomeSource)
                .filter(IncomeSource.invoice_id == invoice.id)
            )
            reused_invoices_w_bpfdata.append((invoice, q.all()))

        return reused_invoices_w_bpfdata

    @classmethod
    def exclude_zero_amount(cls, bpf_data_query):
        """
        Excludes from a query the BusinessBPFData having a total amount (linked invoices) of zero
        :return:
        """
        from caerp.models.training import BusinessBPFData
        from caerp.models.training.bpf import IncomeSource

        filtered_query = (
            bpf_data_query.join(BusinessBPFData.income_sources)
            .join(IncomeSource.invoice)
            .group_by(BusinessBPFData)
            .having(non_null_sum(Invoice.ht) != 0)
            .with_entities(BusinessBPFData)
        )
        return filtered_query


class BusinesssBPFDataMigrator_15to16:
    """
    Tranform Cerfa 10443*15 data into 10443*15 data

    Tries to tranform a BusinessBPFData from 2020 that was (wrongly) filled
    using a 10443*15 form into 10443*16 form data. Does its best, but errors
    could remain.
    """

    # Section A : manual : no mappping required
    # Section B : manual : no mapping required
    # Section C : mapping
    INCOME_SOURCES_MAPPING = {
        0: 0,  # c_ligne_1 → c_ligne_1
        1: 2,  # c_ligne_a → c_ligne_b
        2: 4,  # c_ligne_b → c_ligne_d
        3: 5,  # c_ligne_c → c_ligne_e
        4: 6,  # c_ligne_d → c_ligne_f
        5: 8,  # c_ligne_e → c_ligne_h
        6: 7,  # c_ligne_3 → c_ligne_g
        7: 10,  # c_ligne_4 → c_ligne_3
        8: 20,  # c_ligne_5 → c_ligne_4
        9: 21,  # c_ligne_6 → c_ligne_5
        10: 22,  # c_ligne_7 → c_ligne_6
        11: 23,  # c_ligne_8 → c_ligne_7
        12: 24,  # c_ligne_9 → c_ligne_8
        13: 30,  # c_ligne_10 → c_ligne_9
        14: 31,  # c_ligne_11 → c_ligne_10
        15: 32,  # c_ligne_12 → c_ligne_11
        16: 32,  # c_ligne_13 → c_ligne_11
    }

    # Section D : no change
    # Section E : manual
    # Section F : mapping on TraineeCount
    # f1 : changes : mapping
    TRAINEE_TYPE_MAPPING = {
        0: 0,  # f_1_ligne_a → f_1_ligne_a
        1: 2,  # f_1_ligne_b → f_1_ligne_c /!\
        2: 2,  # f_1_ligne_c → f_1_ligne_c
        3: 3,  # f_1_ligne_d → f_1_ligne_d
        4: 4,  # f_1_ligne_e → f_1_ligne_e
    }
    # f2 : computed values : no mapping required
    # f3 : mapping:
    TRAINING_GOALS_MAPPING = {
        # f_3_ligne_a1 → f3_ligne_a4 : no change except labels : iso-mapping
        0: 0,
        1: 1,
        2: 2,
        3: 3,
        # f_3_ligne_a5 → f3_ligne_a6 : new categories : no mapping
        # f_3_ligne_b → f3_ligne_f : no change but ids renumbered, mapping :
        4: 10,
        5: 11,
        6: 12,
        7: 13,
        8: 14,
    }
    # f_4 : no change : no mapping required

    @classmethod
    def _migrate_income_sources(cls, bpf_data: "BusinessBPFData") -> None:
        for income_source in bpf_data.income_sources:
            income_source.income_category_id = cls.INCOME_SOURCES_MAPPING[
                income_source.income_category_id
            ]
            DBSESSION.merge(income_source)

    @classmethod
    def _migrate_trainee_types(cls, bpf_data: "BusinessBPFData") -> None:
        for trainee_type in bpf_data.trainee_types:
            trainee_type.trainee_type_id = cls.TRAINEE_TYPE_MAPPING[
                trainee_type.trainee_type_id
            ]
            DBSESSION.merge(trainee_type)

    @classmethod
    def migrate(cls, bpf_data: "BusinessBPFData") -> None:
        """
        Mutate the bpf_data, trying to map data (wrongly) filled in a 10443*15 into
        10443*16 form.
        """
        assert bpf_data.cerfa_version == "10443*15"
        assert bpf_data.financial_year == 2020

        bpf_data.cerfa_version = "10443*16"
        cls._migrate_income_sources(bpf_data)
        cls._migrate_trainee_types(bpf_data)

        bpf_data.training_goal_id = cls.TRAINING_GOALS_MAPPING[
            bpf_data.training_goal_id
        ]
        if not bpf_data.remote_headcount:
            bpf_data.remote_headcount = 0

        DBSESSION.merge(bpf_data)
        DBSESSION.flush()

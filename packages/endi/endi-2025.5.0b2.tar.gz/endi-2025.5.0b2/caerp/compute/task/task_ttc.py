"""
Module de calcul des montants des devis/facture saisis en mode TTC

En mode TTC :

    - L'utilisateur saisie des montants TTC

    - la facture est une facture HT

    - Pour chaque ligne on calcule un HT en faisant une TVA inversée sur le TTC

    - Total HT = Arrondi de la somme des HT de chaque ligne (HT calculé via une TVA 
    inversée pour chaque ligne)

    - Total TTC = somme des TTC de chaque ligne

    - Total TVA = Total TTC - Total HT

    - Il se peut que le Total TVA soit différent de la somme des TVA de chaque ligne

    - Le total TVA du PDF peut donc différer d'un centime de ce qu'il y a dans les 
    écritures
"""
import logging
import operator
from caerp.compute import math_utils
from caerp.compute.task.common import (
    CommonTaskCompute,
    CommonGroupCompute,
    CommonLineCompute,
    CommonDiscountLineCompute,
)

logger = logging.getLogger(__name__)


class TaskTtcCompute(CommonTaskCompute):
    """
    class A(TaskTtcCompute):
        pass

    A.total()
    """

    def _adjust_epsilon_difference(self, data_dict: dict, tva_total: int) -> dict:
        """
        Adapte les TVAs pour que ht+tva = ttc

        Ref #3658 : https://framagit.org/caerp/caerp/-/issues/3658

        NB : n'est pas utilisé dans les exports comptables

        :param data_dict: dictionnary of key / value pair where value is an amount of tva
        :param tva_total: Sum of all the tva values (should be computed in other methods)
        """
        total_ht = self.total_ht()
        total_ttc = self.total()
        tva_expected = total_ttc - total_ht
        if tva_total != tva_expected:
            logger.debug(
                f"  + mode TTC on fait un ajustement de Tva de "
                f"{tva_expected - tva_total}/100000"
            )
            # On ajoute le différenciel à la première tva de la liste
            key = list(data_dict.keys())[0]
            data_dict[key] += tva_expected - tva_total
        return data_dict

    def get_tvas(self, with_discounts=True) -> dict:
        """
        Renvoie un les montants de TVA par taux

        Méthode utilisée pour la présentation dans les PDFs

        .. code-block:: python

            # TVA 20% 45€21 , TVA 7% : 4.5€
            {2000: 4521000, 700: 450000}

        Note sur les calculs :

        Afin que le montant total TTC corresponde à la saisie, on adapte parfois les
        taux de TVA pour que la somme des HT + TVA = TTC
        """
        ret_dict = {}
        total = 0
        for group in self.task.line_groups:
            for key, value in list(group.get_tvas().items()):
                val = ret_dict.get(key, 0)
                val += value
                total += value
                ret_dict[key] = val

        if with_discounts:
            for discount in self.task.discounts:
                val = ret_dict.get(discount.tva, 0)
                discount_value = discount.tva_amount()
                total -= discount_value
                val -= discount_value
                ret_dict[discount.tva] = val

            # Ref : https://framagit.org/caerp/caerp/-/issues/3658
            self._adjust_epsilon_difference(ret_dict, total)
        for key in ret_dict:
            ret_dict[key] = self.floor(ret_dict[key])

        return ret_dict

    def get_tvas_by_product(self):
        """
        Renvoie les montants par produit

        Cette méthode est utilisée pour les exports comptables

        Note sur les calculs :

        Ici les tvas sont dispatchées par compte produit, il est possible
        que la somme des TVAs diffère de ce qui est dans le PDF

        Voir le ticket

        Choix sur les règles de calcul expliquant les différences entre get_tvas
        et get_tvas_by_product

        https://framagit.org/caerp/caerp/-/issues/3688
        """
        ret_dict = {}
        total = 0
        for group in self.task.line_groups:
            for key, value in group.get_tvas_by_product().items():
                val = ret_dict.get(key, 0)
                val += value
                total += value
                ret_dict[key] = val

        for discount in self.task.discounts:
            val = ret_dict.get("rrr", 0)
            discount_value = discount.tva_amount()
            total -= discount_value
            val += discount_value
            ret_dict["rrr"] = val

        # Ref #3688
        # self._adjust_epsilon_difference(ret_dict, total)
        for key in ret_dict:
            ret_dict[key] = self.floor(ret_dict[key])

        return ret_dict

    def tva_native_parts(self, with_discounts=True):
        """
        Return amounts by tva in "native" mode (HT or TTC regarding the mode)
        Here it's TTC
        """
        return self.tva_ttc_parts(with_discounts)

    def tva_ht_parts(self, with_discounts=True):
        """
        Return a dict with the HT amounts stored by corresponding tva value
        dict(tva=ht_tva_part,)
        for each tva value
        """
        ret_dict = {}
        lines = []
        for group in self.task.line_groups:
            lines.extend(group.lines)
        ret_dict = self.add_ht_by_tva(ret_dict, lines)
        if with_discounts:
            ret_dict = self.add_ht_by_tva(ret_dict, self.task.discounts, operator.sub)
        return ret_dict

    def tva_ttc_parts(self, with_discounts=True):
        """
        Return a dict with TTC amounts stored by corresponding tva
        """
        ret_dict = {}
        ht_parts = self.tva_ht_parts(with_discounts)
        tva_parts = self.get_tvas(with_discounts)

        for tva_value, amount in list(ht_parts.items()):
            ret_dict[tva_value] = amount + tva_parts.get(tva_value, 0)
        return ret_dict

    def tva_amount(self):
        """
        Compute the sum of the TVAs amount of TVA
        """
        return self.floor(sum(tva for tva in self.get_tvas().values()))

    def total_ht(self):
        """
        compute the HT amount
        """
        total_ht = self.groups_total_ht() - self.discount_total_ht()
        return self.floor(total_ht)

    def total_ttc(self):
        """
        Compute the TTC total
        """
        return sum(group.total_ttc() for group in self.task.line_groups) - sum(
            discount.total() for discount in self.task.discounts
        )

    def total(self):
        """
        Compute TTC after tax removing
        """
        return self.floor(self.total_ttc())


class GroupTtcCompute(CommonGroupCompute):
    """
    Computing tool for group ttc objects
    """

    pass


class LineTtcCompute(CommonLineCompute):
    """
    Computing tool for line ttc objects
    """

    def unit_ht(self) -> int:
        """
        Compute the unit ht value of the current task line based on its ttc
        unit value
        """
        return math_utils.compute_ht_from_ttc(
            self.unit_ttc(),
            self.task_line.tva,
            float_format=False,
        )

    def unit_ttc(self) -> int:
        return self.task_line.cost or 0

    def total_ht(self):
        """
        Compute the line's ht total

        :rtype: int
        """
        result = self.unit_ht() * self._get_quantity()
        return result

    def tva_amount(self):
        """
        compute the tva amount of a line
        :rtype: int
        """
        return self.total() - self.total_ht()

    def total(self):
        """
        Compute the ttc amount of the line
        :rtype: int
        """
        quantity = self._get_quantity()
        cost = self.task_line.cost or 0
        return cost * quantity


class DiscountLineTtcCompute(CommonDiscountLineCompute):
    """
    Computing tool for discount line ttc objects
    """

    def total_ht(self):
        """
        compute round total ht amount of a line
        """
        total_ttc = self.total()
        result = math_utils.compute_ht_from_ttc(
            total_ttc,
            self.discount_line.tva,
            float_format=False,
        )
        return result

    def tva_amount(self):
        """
        compute the tva amount of a line
        """
        total_ttc = self.total()
        total_ht = self.total_ht()
        return total_ttc - total_ht

    def total(self):
        """
        :return: float ttc amount of a line
        """
        return self.discount_line.amount

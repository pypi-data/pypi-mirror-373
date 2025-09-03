"""
    Task computing tool
    Used to compute invoice, estimation or cancelinvoice totals
"""
import operator
import logging

from caerp.models.tva import Tva
from caerp.compute import math_utils
from caerp.compute.task.common import (
    CommonTaskCompute,
    CommonGroupCompute,
    CommonLineCompute,
    CommonDiscountLineCompute,
)

logger = logging.getLogger(__name__)


def get_default_tva():
    """
    Return the default tva
    """
    try:
        default_tva = Tva.get_default()
    except Exception:
        default_tva = None

    if default_tva:
        return default_tva.value
    else:
        return 2000


class TaskCompute(CommonTaskCompute):
    """
    class A(TaskCompute):
        pass

    A.total()
    """

    # Expense HT computing : Doesn't exist anymore
    def expenses_amount(self):
        """
        return the amount of the expenses
        """
        expenses = self.task.expenses or 0
        result = int(expenses)
        return result

    def get_expenses_tva(self):
        """
        Return the tva for the HT expenses
        """
        expenses_tva = getattr(self.task, "expenses_tva", -1)
        if expenses_tva == -1:
            self.task.expenses_tva = get_default_tva()
        return self.task.expenses_tva

    def get_expense_ht(self):
        """
        Return a line object for the HT expense handling
        """
        # We should not use a TaskLine here, but a TaskLineCompute
        from caerp.models.task import TaskLine

        return TaskLine(
            tva=self.get_expenses_tva(),
            cost=self.task.expenses_ht,
            quantity=1,
            mode="ht",
        )

    # TVA computing
    def get_tvas(self, with_discounts=True):
        """
        return a dict with the tvas amounts stored by tva
        {1960:450.56, 700:45}
        """
        expense = None

        ret_dict = {}
        for group in self.task.line_groups:
            for key, value in list(group.get_tvas().items()):
                val = ret_dict.get(key, 0)
                val += value
                ret_dict[key] = val

        if with_discounts:
            for discount in self.task.discounts:
                val = ret_dict.get(discount.tva, 0)
                val -= discount.tva_amount()
                ret_dict[discount.tva] = val

        expenses_ht = getattr(self.task, "expenses_ht", 0)
        tva_amount = 0
        if expenses_ht != 0:
            expense = self.get_expense_ht()
            tva_amount = expense.tva_amount()

        if tva_amount != 0 and expense is not None:
            val = ret_dict.get(expense.tva, 0)

            val += expense.tva_amount()
            ret_dict[expense.tva] = val

        for key in ret_dict:
            ret_dict[key] = self.floor(ret_dict[key])
        return ret_dict

    def get_tvas_by_product(self) -> dict:
        """
        Return tvas stored by product type
        """
        ret_dict = {}
        for group in self.task.line_groups:
            for key, value in group.get_tvas_by_product().items():
                val = ret_dict.get(key, 0)
                val += value
                ret_dict[key] = val

        for discount in self.task.discounts:
            val = ret_dict.get("rrr", 0)
            val += discount.tva_amount()
            ret_dict["rrr"] = val

        expense_ht = getattr(self.task, "expenses_ht", 0)
        tva_amount = 0
        if expense_ht != 0:
            expense = self.get_expense_ht()
            tva_amount = expense.tva_amount()

        if tva_amount > 0:
            val = ret_dict.get("expense", 0)
            val += tva_amount
            ret_dict["expense"] = val

        for key in ret_dict:
            ret_dict[key] = self.floor(ret_dict[key])

        return ret_dict

    def tva_native_parts(self, with_discounts=True):
        """
        Return a dict with the HT amounts stored by corresponding tva value
        dict(tva=tva_part,)
        for each tva value *in native compute mode* (eg: HT when task.mode == 'ht')
        """
        return self.tva_ht_parts(with_discounts)

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
        expense = self.get_expense_ht()
        if expense.cost != 0:
            ret_dict = self.add_ht_by_tva(ret_dict, [expense])
        return ret_dict

    def tva_ttc_parts(self, with_discounts=True):
        """
        Return a dict with TTC amounts stored by corresponding tva
        """
        ret_dict = {}
        ht_parts = self.tva_ht_parts(with_discounts)
        tva_parts = self.get_tvas(with_discounts)

        for tva_value, amount in ht_parts.items():
            ret_dict[tva_value] = amount + tva_parts.get(tva_value, 0)
        return ret_dict

    def tva_amount(self):
        """
        Compute the sum of the TVAs amount of TVA
        """
        return self.floor(sum(tva for tva in list(self.get_tvas().values())))

    def total_ht(self):
        """
        compute the HT amount
        """
        expenses_ht = getattr(self.task, "expenses_ht") or 0  # TODO refactore
        total_ht = self.groups_total_ht() - self.discount_total_ht() + expenses_ht
        return self.floor(total_ht)

    def total_ttc(self):
        """
        Compute the TTC total
        """
        return self.total_ht() + self.tva_amount()

    def total(self):
        """
        Compute TTC after tax removing
        """
        return self.total_ttc() + self.expenses_amount()


class GroupCompute(CommonGroupCompute):
    task_line_group = None

    def total_ttc(self):
        """
        Returns the TTC total for this group
        """
        return self.total_ht() + self.tva_amount()


class LineCompute(CommonLineCompute):
    """
    Computing tool for line objects
    """

    def unit_ht(self) -> int:
        return self.task_line.cost

    def unit_ttc(self) -> int:
        if self.task_line.tva:
            unit_tva = math_utils.compute_tva(self.unit_ht(), self.task_line.tva)
        else:
            unit_tva = 0
        return self.unit_ht() + unit_tva

    def total_ht(self):
        """
        Compute the line's total
        """
        cost = self.task_line.cost or 0
        quantity = self._get_quantity()
        return cost * quantity

    def tva_amount(self):
        """
        compute the tva amount of a line
        """
        total_ht = self.total_ht()
        if self.task_line.tva:
            return math_utils.compute_tva(total_ht, self.task_line.tva)
        else:
            return 0

    def total(self):
        """
        Compute the ttc amount of the line
        """
        return self.tva_amount() + self.total_ht()


class DiscountLineCompute(CommonDiscountLineCompute):
    """
    Computing tool for discount_line objects
    """

    def total_ht(self):
        return float(self.discount_line.amount)

    def tva_amount(self):
        """
        compute the tva amount of a line
        """
        total_ht = self.total_ht()
        return math_utils.compute_tva(total_ht, self.discount_line.tva)

    def total(self):
        return self.tva_amount() + self.total_ht()

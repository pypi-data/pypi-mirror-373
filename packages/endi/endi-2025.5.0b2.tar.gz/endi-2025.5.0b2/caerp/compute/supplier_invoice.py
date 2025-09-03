from caerp.compute import math_utils
from caerp.compute.base_line import BaseLineCompute
from caerp.models.expense.types import ExpenseType


class SupplierInvoiceCompute:
    """
    Handles numbers as decimal stored as int with 2 decimals.

    lines : SupplierOrderLine[]
    cae_percentage: int
    """

    supplier_orders = ()
    lines = ()
    payments = ()
    supplier_sepa_waiting_payments = ()
    user_sepa_waiting_payments = ()

    @property
    def orders_total(self) -> int:
        return sum(order.total for order in self.supplier_orders)

    @property
    def orders_cae_total(self) -> int:
        return sum(order.cae_total for order in self.supplier_orders)

    @property
    def orders_worker_total(self) -> int:
        return sum(order.worker_total for order in self.supplier_orders)

    @property
    def orders_total_ht(self) -> int:
        return sum(order.total_ht for order in self.supplier_orders)

    @property
    def orders_total_tva(self) -> int:
        return sum(order.total_tva for order in self.supplier_orders)

    @property
    def total(self) -> int:
        return sum([line.total for line in self.lines])

    @property
    def total_ht(self) -> int:
        return sum([line.total_ht for line in self.lines])

    @property
    def total_tva(self) -> int:
        return sum([line.total_tva for line in self.lines])

    @property
    def cae_total(self) -> int:
        cae_total_as_integer = math_utils.floor_to_precision(
            self.total * self.cae_percentage / 100,
            precision=2,
            dialect_precision=2,
        )
        return cae_total_as_integer

    @property
    def worker_total(self) -> int:
        return self.total - self.cae_total

    def topay(self) -> int:
        value = self.total - self.paid()
        if self.total > 0:
            return max(value, 0)
        else:
            return min(value, 0)

    def cae_topay(self) -> int:
        value = self.cae_total - self.cae_paid()
        if self.total > 0:
            return max(value, 0)
        else:
            return min(value, 0)

    def worker_topay(self) -> int:
        value = self.worker_total - self.worker_paid()
        if self.total > 0:
            return max(value, 0)
        else:
            return min(value, 0)

    def paid(self) -> int:
        return sum([payment.get_amount() for payment in self.payments])

    def cae_paid(self) -> int:
        return sum([payment.get_amount() for payment in self.cae_payments])

    def worker_paid(self) -> int:
        return sum([payment.get_amount() for payment in self.user_payments])

    def cae_sepa_waiting_amount(self) -> int:
        """Amount already waiting for being inserted in SEPA order"""
        return sum(
            [
                payment.amount
                for payment in self.supplier_sepa_waiting_payments
                if payment.paid_status == payment.WAIT_STATUS
            ]
        )

    def worker_sepa_waiting_amount(self) -> int:
        """Amount available to be inserted in SEPA order"""
        return sum(
            [
                payment.amount
                for payment in self.user_sepa_waiting_payments
                if payment.paid_status == payment.WAIT_STATUS
            ]
        )

    def cae_amount_waiting_for_payment(self) -> int:
        """Amount available to be inserted in SEPA order"""
        return self.cae_topay() - self.cae_sepa_waiting_amount()

    def worker_amount_waiting_for_payment(self) -> int:
        """Amount available to be inserted in SEPA order"""
        return self.worker_topay() - self.worker_sepa_waiting_amount()

    def amount_waiting_for_payment(self) -> int:
        return (
            self.worker_amount_waiting_for_payment()
            + self.cae_amount_waiting_for_payment()
        )

    def get_lines_by_type(self):
        """
        Return supplier invoice lines grouped by treasury code
        """
        ret_dict = {}
        for line in self.lines:
            line.type_object = ExpenseType.query().filter_by(id=line.type_id).first()
            ret_dict.setdefault(line.type_object.code, []).append(line)
        return list(ret_dict.values())


class SupplierInvoiceLineCompute(BaseLineCompute):
    @property
    def cae_total(self) -> int:
        cae_total_as_integer = math_utils.floor_to_precision(
            self.total * self.supplier_invoice.cae_percentage / 100,
            precision=2,
            dialect_precision=2,
        )
        return cae_total_as_integer

    @property
    def worker_total(self) -> int:
        return self.total - self.cae_total

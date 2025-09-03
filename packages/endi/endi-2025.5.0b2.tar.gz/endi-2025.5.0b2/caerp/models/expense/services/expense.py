from caerp.models.services.mixins import BusinessLinkedServiceMixin


class BaseExpenseLineService(BusinessLinkedServiceMixin):
    def total_expense(
        cls,
        query_filters=[],
        column_name="total_ht",
        tva_on_margin: bool = None,
    ):
        from caerp.models.expense.sheet import (
            ExpenseLine,
            ExpenseKmLine,
        )
        from caerp.models.expense.types import ExpenseType

        query = cls.query()
        query = query.with_polymorphic([ExpenseLine, ExpenseKmLine])

        if tva_on_margin is not None:
            query = query.join(cls.expense_type)
            # include or exclude
            query = query.filter(ExpenseType.tva_on_margin == tva_on_margin)

        if query_filters:
            query = query.filter(*query_filters)
        return sum(getattr(e, column_name) for e in query.all())

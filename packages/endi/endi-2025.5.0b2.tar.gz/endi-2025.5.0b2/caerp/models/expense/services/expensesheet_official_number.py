from sqlalchemy import func, select
from caerp.models.sequence_number import (
    GlobalSequence,
    MonthCompanySequence,
    MonthSequence,
    SequenceNumber,
    YearSequence,
)

from caerp.models.services.official_number import AbstractNumberService


class ExpMonthSequence(MonthSequence):
    def _query(self, node):
        q = super(MonthSequence, self)._query(node)
        q = q.filter(self.model_class.month == node.month)
        return q


class ExpMonthCompanySequence(MonthCompanySequence):
    def __init__(self, *args, **kwargs):
        self.company_init_date_fieldname = kwargs.pop(
            "company_init_date_fieldname", None
        )
        self.company_init_value_fieldname = kwargs.pop(
            "company_init_value_fieldname", None
        )
        super(ExpMonthCompanySequence, self).__init__(
            *args,
            **kwargs,
        )

    def _get_initial_value(self, node):
        if (
            self.company_init_date_fieldname is None
            or self.company_init_value_fieldname is None
        ):
            return None
        init_date = getattr(node.company, self.company_init_date_fieldname)
        init_value = getattr(node.company, self.company_init_value_fieldname)
        if (
            init_date
            and init_value
            and init_date.year == node.validation_date.year
            and init_date.month == node.validation_date.month
        ):
            return init_value
        else:
            return None

    def _query(self, node):
        q = super(ExpMonthCompanySequence, self)._query(node)
        q = q.filter(self.model_class.month == node.month)
        q = q.filter(self.model_class.company == node.company)
        return q


class ExpenseSheetNumberService(AbstractNumberService):
    lock_name = "expense_sheet_number"

    @classmethod
    def get_sequences_map(cls):
        from caerp.models.expense.sheet import ExpenseSheet

        seq_kwargs = dict(
            types=["expensesheet"],
            model_class=ExpenseSheet,
        )
        return {
            "SEQGLOBAL": GlobalSequence(
                db_key=SequenceNumber.SEQUENCE_EXPENSESHEET_GLOBAL,
                init_value_config_key="global_expensesheet_sequence_init_value",
                **seq_kwargs,
            ),
            "SEQYEAR": YearSequence(
                db_key=SequenceNumber.SEQUENCE_EXPENSESHEET_YEAR,
                init_value_config_key="year_expensesheet_sequence_init_value",
                init_date_config_key="year_expensesheet_sequence_init_date",
                **seq_kwargs,
            ),
            "SEQMONTH": ExpMonthSequence(
                db_key=SequenceNumber.SEQUENCE_EXPENSESHEET_MONTH,
                init_value_config_key="month_expensesheet_sequence_init_value",
                init_date_config_key="month_expensesheet_sequence_init_date",
                **seq_kwargs,
            ),
            "SEQMONTHANA": ExpMonthCompanySequence(
                db_key=SequenceNumber.SEQUENCE_EXPENSESHEET_MONTH_COMPANY,
                **seq_kwargs,
            ),
        }

    @classmethod
    def is_already_used(cls, request, node_id, official_number) -> bool:
        # NB : On accède à l'engine pour effectuer notre requête en dehors de la
        # transaction : cf https://framagit.org/caerp/caerp/-/issues/2811
        engine = request.dbsession.connection().engine

        # Imported here to avoid circular dependencies
        from caerp.models.expense.sheet import ExpenseSheet

        sql = select(func.count(ExpenseSheet.id))

        sql = sql.where(
            ExpenseSheet.official_number == official_number,
            ExpenseSheet.id != node_id,
        )
        query = engine.execute(sql)
        return query.scalar() > 0

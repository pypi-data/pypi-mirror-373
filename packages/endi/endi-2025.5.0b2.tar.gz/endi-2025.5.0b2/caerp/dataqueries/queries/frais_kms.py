from caerp.dataqueries.base import BaseDataQuery
from caerp.models.expense.sheet import ExpenseKmLine, ExpenseSheet
from caerp.models.expense.types import ExpenseKmType
from caerp.utils import strings
from caerp.utils.dataqueries import dataquery_class


@dataquery_class()
class FraisKmsQuery(BaseDataQuery):

    name = "frais_kms"
    label = "Détail des frais kms sur la période"
    description = """
    Liste de tous les frais kms validés sur la période.
    """

    def default_dates(self):
        self.start_date = self.date_tools.year_start()
        self.end_date = self.date_tools.year_end()

    def headers(self):
        headers = [
            "Entrepreneur",
            "Date",
            "Type",
            "Motif",
            "Départ",
            "Arrivée",
            "Nb kms",
            "Taux",
            "Indemnités",
        ]
        return headers

    def data(self):
        data = []

        km_types = ExpenseKmType.query().order_by(
            ExpenseKmType.year, ExpenseKmType.amount
        )
        km_lines = (
            ExpenseKmLine.query()
            .join(ExpenseSheet)
            .filter(ExpenseSheet.status == "valid")
            .filter(ExpenseKmLine.date.between(self.start_date, self.end_date))
            .order_by(ExpenseKmLine.date)
        )
        for l in km_lines:
            rate = round(l.ht / l.km, 4) if l.km != 0 else 0
            type_label = ""
            for t in km_types:
                if t.year == l.date.year and t.amount == rate:
                    type_label = t.label
            data.append(
                [
                    f"{l.sheet.user.lastname} {l.sheet.user.firstname}",
                    strings.format_date(l.date),
                    type_label,
                    l.description,
                    l.start,
                    l.end,
                    strings.format_amount(l.km, grouping=False),
                    rate,
                    strings.format_amount(l.ht, grouping=False),
                ]
            )

        return data

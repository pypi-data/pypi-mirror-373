from caerp_base.models import DBSESSION
from sqlalchemy import func

from caerp.models.task import (
    TaskLine,
    Invoice,
    TaskLineGroup,
)
from caerp.models.tva import Product
from caerp.plugins.sap.models.services.subqueries import (
    _subqueries,
)
from caerp.sql_compute.task.task import TaskLineSqlCompute


def zero_or_null(field):
    """
    Avoids using a .in_((v1, v2…)) which do not support NULL values
    sqla helper
    """
    return (field == 0) | (field == None)  # noqa


class NovaStatsService:
    """
    Stats pour le service nova

    https://www.servicesalapersonne.gouv.fr/files_sap/files/professionnels/nova/tutoriel_nova.pdf
    """

    @classmethod
    def query(cls):
        # Supports only HT mode
        ht = func.ifnull(TaskLine.quantity, 1) * func.ifnull(TaskLine.cost, 0)
        query = DBSESSION().query(
            TaskLine.month.label("month"),
            TaskLine.year,
            TaskLine.product_id.label("product_id"),
            func.count(Invoice.customer_id.distinct()).label("customers_count"),
            func.count(Invoice.company_id.distinct()).label("company_count"),
            Product.name.label("product_name"),
            func.sum(func.IF(TaskLine.is_in_hours, TaskLine.quantity, 0)).label(
                "invoiced_hours"
            ),
            # Proratize the discounts and negative tasklines among positive
            # tasklines
            func.sum(
                TaskLineSqlCompute.total_ht
                * Invoice.ht
                / _subqueries.discount_ratio.c.positive_lines_sum
            ).label("reported_total_ht"),
        )
        query = query.join(
            Product,
            TaskLine.product_id == Product.id,
        )
        query = query.join(
            TaskLineGroup,
            TaskLine.group_id == TaskLineGroup.id,
        )
        query = query.join(Invoice)
        query = query.join(_subqueries.discount_ratio)
        query = query.outerjoin(_subqueries.cancelinvoices_summary)

        query = query.filter(
            # exclude the canceled invoices
            zero_or_null(_subqueries.cancelinvoices_summary.c.ttc),
            Invoice.status == "valid",
            TaskLine.cost > 0,
            # Exclude internal invoices / cancelinvoices
            Invoice.type_ == "invoice",
        )
        return query

    @classmethod
    def query_for_monthly_summary(cls, year):
        query = cls.query()
        query = query.filter(
            TaskLine.year == year,
        )
        query = query.group_by(
            TaskLine.year,
            TaskLine.month,
        )
        return query

    @classmethod
    def query_for_yearly_summary(cls, year):
        query = cls.query()
        query = query.filter(
            TaskLine.year == year,
        )
        return query

    @classmethod
    def query_for_year(cls, year):
        query = cls.query()
        query = query.filter(
            TaskLine.year == year,
        )
        query = query.group_by(
            TaskLine.year,
            TaskLine.product_id,
        )
        return query

    @classmethod
    def query_for_product(cls, year, product_id):
        query = cls.query()
        query = query.filter(
            TaskLine.year == year,
            TaskLine.product_id == product_id,
        )
        query = query.group_by(
            TaskLine.year,
            TaskLine.month,
            TaskLine.product_id,
        )
        return query

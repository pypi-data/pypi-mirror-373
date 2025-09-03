import datetime
from sqlalchemy import select, func
from typing import List, Optional
from caerp.consts.rgpd import RGPD_CUSTOMER_LABEL, RGPD_DEFAULT_CUSTOMER_RETENTION_DAYS
from caerp.services.rgpd.utils import get_retention_days
from caerp.models.third_party import Customer
from caerp.models.task import Task


def get_customers_not_used_for(request, days_threshold: int) -> List[Customer]:
    """
    Collect individual customers not attached to any Task object more recent
    dans days_threshold days.
    """
    reference_date = datetime.datetime.today() - datetime.timedelta(days=days_threshold)
    subq = (
        select(Task.customer_id, func.max(Task.date).label("maxdate"))
        .group_by(Task.customer_id)
        .subquery()
    )
    query = (
        select(Customer)
        .join(subq, Customer.id == subq.c.customer_id)
        .where(Customer.label != RGPD_CUSTOMER_LABEL)
        .where(Customer.type == "individual")
        .where(subq.c.maxdate < reference_date)
        .where(
            Customer.created_at < reference_date,  # type: ignore
        )
    )
    return request.dbsession.execute(query).scalars().all()


def check_customer_expired(
    request, customer_id: int, days_threshold: Optional[int] = None
) -> bool:
    """
    Check if the customer is not attached to any Task object more recent
    than the configured retention period.
    """
    customer = request.dbsession.execute(
        select(Customer).where(Customer.id == customer_id)
    ).scalar()
    if not customer or customer.type != "individual":
        # Pas un particulier
        return False
    if customer.label == RGPD_CUSTOMER_LABEL:
        # Déjà anonymisé
        return False

    if days_threshold is None:
        days_threshold = get_retention_days(
            request, "customer", RGPD_DEFAULT_CUSTOMER_RETENTION_DAYS
        )
    reference_date = datetime.date.today() - datetime.timedelta(days=days_threshold)
    maxdate = request.dbsession.execute(  # type: ignore
        select(func.max(Task.date)).where(
            Task.customer_id == customer_id
        )  # type: ignore
    ).scalar()

    if maxdate and maxdate > reference_date:
        return False
    else:
        if customer.created_at.date() < reference_date:  # type: ignore
            return True
        return False

import datetime
import logging

from dateutil.relativedelta import relativedelta
from typing import Union
from sqlalchemy import (
    distinct,
    func,
    select,
)

from caerp.models.accounting.operations import AccountingOperation
from caerp.models.config import Config
from caerp.models.third_party import Customer
from caerp.models.tva import Tva


logger = logging.getLogger(__name__)


ACCOUNTING_SOFTWARES = [
    (None, "Non défini"),
    ("sage", "SAGE"),
    ("sage_experts", "SAGE GENERATION EXPERTS"),
    ("quadra", "QUADRA / CEGID"),
    ("isacompta", "ISACOMPTA"),
    ("ibiza", "IBIZA"),
    ("ebp", "EBP"),
    ("ciel", "CIEL"),
    ("cador", "CADOR"),
]


def get_accounting_closure_values() -> "tuple[int,int]":
    """
    Return the day and month of the configured accounting closure
    """
    closure_day = Config.get_value("accounting_closure_day", default=31, type_=int)
    closure_month = Config.get_value("accounting_closure_month", default=12, type_=int)
    return closure_day, closure_month


def get_financial_year_data(
    year: Union[int, str] = datetime.date.today().year,
) -> dict:
    """
    Compute usefull data for a given financial year
    according to accounting closure config

    param int|str year : The END'S YEAR of the financial year we want

    :returns: A dict with all usefull data of the financial year
    {
        "label": str = Financial year global label ("yyyy" or "yyyy/yy")
        "start_date": str = Financial year start date ("yyyy-mm-dd")
        "start_year": int = Financial year start year (yyyy)
        "start_month": int = Financial year start month (m)
        "start_label": str = Financial year start label ("dd/mm/yyyy")
        "end_date": str = Financial year end date ("yyyy-mm-dd")
        "end_year": int = Financial year end year (yyyy)
        "end_month": int = Financial year end month (m)
        "end_label": str = Financial year end label ("dd/mm/yyyy")
    }
    """
    closure_day, closure_month = get_accounting_closure_values()
    if isinstance(year, str):
        year = int(year)
    end_date = datetime.date(year, closure_month, closure_day)
    start_date = end_date - relativedelta(years=1) + relativedelta(days=1)
    label = str(start_date.year)
    if end_date.year != start_date.year:
        label += "/{}".format(end_date.strftime("%y"))
    return {
        "label": label,
        "start_date": start_date,
        "start_year": start_date.year,
        "start_month": start_date.month,
        "start_label": start_date.strftime("%d/%m/%Y"),
        "end_date": end_date,
        "end_year": end_date.year,
        "end_month": end_date.month,
        "end_label": end_date.strftime("%d/%m/%Y"),
    }


def get_current_financial_year_data() -> dict:
    """
    Return usefull data on the current financial year
    """
    today = datetime.date.today()
    closure_day, closure_month = get_accounting_closure_values()
    year = today.year
    if today.month > closure_month or (
        today.month == closure_month and today.day > closure_day
    ):
        year += 1
    return get_financial_year_data(year)


def get_previous_financial_year_data() -> dict:
    """
    Return usefull data on the previous financial year
    """
    today = datetime.date.today()
    closure_day, closure_month = get_accounting_closure_values()
    year = today.year - 1
    if today.month > closure_month or (
        today.month == closure_month and today.day > closure_day
    ):
        year += 1
    return get_financial_year_data(year)


def get_current_financial_year_value() -> int:
    """
    Return the year value (end's year) of the current financial year
    """
    today = datetime.date.today()
    current_financial_year = today.year
    closure_day, closure_month = get_accounting_closure_values()
    if today.month > closure_month or (
        today.month == closure_month and today.day > closure_day
    ):
        current_financial_year += 1
    return current_financial_year


def get_all_financial_year_values(request, cls=AccountingOperation) -> list:
    """
    Return the year values (end's year) of the known financial years
    """
    query = select(distinct(func.extract("YEAR", cls.date))).order_by(cls.date.desc())
    years = request.dbsession.execute(query).scalars().all()

    if get_current_financial_year_value() not in years:
        years.insert(0, get_current_financial_year_value())
    return years


def get_cae_accounting_software() -> "tuple[str, str]":
    """
    Return id and label of configured CAE's accounting software
    """
    cae_accounting_software = Config.get_value("accounting_software")
    for software_id, software_label in ACCOUNTING_SOFTWARES:
        if software_id == cae_accounting_software:
            return (software_id, software_label)
    return ACCOUNTING_SOFTWARES[0]


def is_thirdparty_account_mandatory_for_users(request) -> bool:
    """
    Return if third party accounts are mandatory for users
    """
    return request.config.get_value("thirdparty_account_mandatory_user", False, bool)


def is_thirdparty_account_mandatory_for_customers(request) -> bool:
    """
    Return if third party accounts are mandatory for customers
    """
    return request.config.get_value(
        "thirdparty_account_mandatory_customer", False, bool
    )


def is_thirdparty_account_mandatory_for_suppliers(request) -> bool:
    """
    Return if third party accounts are mandatory for suppliers
    """
    return request.config.get_value(
        "thirdparty_account_mandatory_supplier", False, bool
    )


def is_customer_accounting_by_tva(request) -> bool:
    """
    Return if we use customer accounts by TVA
    """
    return request.config.get_value(
        "bookentry_sales_customer_account_by_tva", False, bool
    )


def get_customer_accounting_general_account(
    request, customer_id: int, tva_id: int = None, prefix: str = ""
) -> str:
    """
    Retourne le compte client à utiliser en fonction de la configuration de l'instance
    """
    if tva_id is not None:
        tva = request.dbsession.get(Tva, tva_id)
        if tva:
            if is_customer_accounting_by_tva(request):
                return tva.compte_client

    customer = request.dbsession.get(Customer, customer_id)
    return customer.get_general_account(prefix=prefix)


def check_customer_accounting_configuration(request, customer, invoice) -> bool:
    """
    Check if the invoice's customer is well configured for exports
    """
    prefix = "internal" if invoice.internal else ""

    for tva_val in invoice.get_tvas():
        tva = Tva.by_value(tva_val)
        if not get_customer_accounting_general_account(
            request, customer.id, tva.id, prefix
        ):
            return False

    if is_thirdparty_account_mandatory_for_customers(request):
        if not customer.get_third_party_account(prefix):
            return False

    return True


def check_user_accounting_configuration(request, user) -> bool:
    """
    Check if the user is well configured for exports
    """
    if is_thirdparty_account_mandatory_for_users(request):
        if not user.compte_tiers:
            return False

    return True


def check_company_accounting_configuration(company) -> bool:
    """
    Check if the company is well configured for exports
    """
    if not company.code_compta:
        return False

    return True


def check_waiver_accounting_configuration(request) -> bool:
    """
    Check if the waiver cg account is well configured for exports
    """
    if not request.config.get("compte_cg_waiver_ndf"):
        return False

    return True

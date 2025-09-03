import logging
import colander
from caerp.consts.permissions import PERMISSIONS
from sqlalchemy import distinct

from caerp_base.models.base import DBSESSION
from caerp.forms.validation.expenses import get_list_schema
from caerp.models.expense.sheet import ExpenseSheet
from caerp.models.user import User, UserDatas
from caerp.resources import admin_expense_js
from caerp.views import BaseListView


logger = logging.getLogger(__name__)


class ExpensesValidationView(BaseListView):
    title = "Notes de dépenses en attente de validation"
    sort_columns = dict(
        status_date=ExpenseSheet.status_date,
        month=ExpenseSheet.month,
        name=User.lastname,
    )
    add_template_vars = ("title",)
    default_sort = "status_date"
    default_direction = "desc"

    def get_schema(self):
        return get_list_schema(self.request)

    def query(self):
        admin_expense_js.need()
        query = DBSESSION().query(distinct(ExpenseSheet.id), ExpenseSheet)
        query = query.outerjoin(ExpenseSheet.user)
        query = query.outerjoin(User.userdatas)
        query = query.order_by(ExpenseSheet.year.desc())
        query = query.filter(ExpenseSheet.status == "wait")
        return query

    def filter_year(self, query, appstruct):
        year = appstruct.get("year")
        if year and year not in (-1, colander.null):
            query = query.filter(ExpenseSheet.year == year)
        return query

    def filter_month(self, query, appstruct):
        month = appstruct.get("month")
        if month and month not in (-1, colander.null, "-1"):
            query = query.filter(ExpenseSheet.month == month)
        return query

    def filter_owner(self, query, appstruct):
        user_id = appstruct.get("owner_id", None)
        if user_id and user_id not in ("", -1, colander.null):
            query = query.filter(ExpenseSheet.user_id == user_id)
        return query

    def filter_doc_status(self, query, appstruct):
        status = appstruct.get("justified_status")
        if status == "notjustified":
            query = query.filter(ExpenseSheet.justified == False)
        elif status == "justified":
            query = query.filter(ExpenseSheet.justified == True)
        return query

    def filter_follower(self, query, appstruct):
        follower_id = appstruct.get("follower_id", None)
        if follower_id and follower_id not in ("", -1, colander.null):
            query = query.filter(UserDatas.situation_follower_id == follower_id)
        return query

    def filter_antenne_id(self, query, appstruct):
        antenne_id = appstruct.get("antenne_id")
        if antenne_id not in (None, colander.null):
            query = query.filter(UserDatas.situation_antenne_id == antenne_id)
        return query


def includeme(config):
    config.add_route("validation_expenses", "validation/expenses")
    config.add_view(
        ExpensesValidationView,
        route_name="validation_expenses",
        renderer="validation/expenses.mako",
        permission=PERMISSIONS["global.validate_expensesheet"],
    )
    config.add_admin_menu(
        parent="validation",
        order=2,
        label="Notes de dépenses",
        href="/validation/expenses",
        permission=PERMISSIONS["global.validate_expensesheet"],
    )

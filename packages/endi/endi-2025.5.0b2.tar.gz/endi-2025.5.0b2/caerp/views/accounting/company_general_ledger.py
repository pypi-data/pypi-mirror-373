import datetime
import colander
import logging

from sqlalchemy.orm import load_only
from sqlalchemy import and_, not_, or_

from caerp.consts.permissions import PERMISSIONS
from caerp.forms.accounting import get_company_general_ledger_operations_list_schema
from caerp.models.accounting.general_ledger_account_wordings import (
    GeneralLedgerAccountWording,
)
from caerp.models.accounting.operations import (
    AccountingOperationUpload,
    AccountingOperation,
)
from caerp.models.config import Config
from caerp.models.company import Company
from caerp.views import BaseListView
from caerp.views.accounting.routes import COMPANY_GENERAL_LEDGER_OPERATION


logger = logging.getLogger(__name__)


class CompanyGeneralLedgerOperationsListTools:
    """
    Tools for general legder uploads for the current company
    """

    schema = get_company_general_ledger_operations_list_schema()
    sort_columns = {
        "general_account": AccountingOperation.general_account,
        "date": AccountingOperation.date,
    }
    default_sort = "date"
    default_direction = "desc"

    @property
    def title(self):
        return f"Grand livre"

    @property
    def title_detail(self):
        return f"(enseigne {self.context.name})"

    def get_company_id(self):
        """
        Return the company_id from which to fetch the grids. If there is multiple
        companies with the same analytical account we use the oldest company.
        """
        return Company.get_id_by_analytical_account(self.context.code_compta)

    def query(self):
        accounting_operation_upload_query = AccountingOperationUpload.query().filter(
            AccountingOperationUpload.filetype.in_(
                ["general_ledger", "synchronized_accounting"]
            )
        )
        uploads_ids = [u.id for u in accounting_operation_upload_query]

        query = AccountingOperation.query().options(
            load_only(
                AccountingOperation.id,
                AccountingOperation.analytical_account,
                AccountingOperation.general_account,
                AccountingOperation.company_id,
                AccountingOperation.label,
                AccountingOperation.debit,
                AccountingOperation.credit,
                AccountingOperation.balance,
                AccountingOperation.upload_id,
                AccountingOperation.date,
            )
        )
        return query.filter(
            and_(
                AccountingOperation.company_id == self.get_company_id(),
                AccountingOperation.upload_id.in_(uploads_ids),
            )
        )

    def filter_cae_config_general_account(self, query, appstruct):
        """
        Filter general_account from cae configuration
        :param query:
        :param appstruct:
        :return: query
        """
        company_general_ledger_accounts_filter = Config.get_value(
            "company_general_ledger_accounts_filter", None
        )
        if company_general_ledger_accounts_filter is None:
            return query

        accounts = [
            account.strip()
            for account in company_general_ledger_accounts_filter.split(",")
        ]

        negative_accounts = [account for account in accounts if account.startswith("-")]
        positive_accounts = [
            account
            for account in accounts
            if account != "" and account not in negative_accounts
        ]

        # cleaning negative sign
        negative_accounts = [account.replace("-", "") for account in negative_accounts]
        # filter or on authorized accounts
        if len(positive_accounts) > 0:
            query = query.filter(
                or_(
                    AccountingOperation.general_account.startswith(account)
                    for account in positive_accounts
                )
            )
        # filter on unauthorized accounts
        if len(negative_accounts) > 0:
            for account in negative_accounts:
                query = query.filter(
                    not_(AccountingOperation.general_account.startswith(account))
                )
        return query

    def filter_general_account(self, query, appstruct):
        """
        Filter general_account from filter form
        :param query:
        :param appstruct:
        :return: query
        """
        account = appstruct.get("general_account")
        if account not in ("", colander.null, None):
            logger.debug("    + Filtering by general_account")
            query = query.filter_by(general_account=account)
        return query

    def filter_date(self, query, appstruct):
        period = appstruct.get("period", {})
        if period.get("start") not in (colander.null, None):
            logger.debug("  + Filtering by date : %s" % period)
            start = period.get("start")
            end = period.get("end")
            if end in (None, colander.null):
                end = datetime.date.today()
            query = query.filter(AccountingOperation.date.between(start, end))
        return query

    def filter_debit(self, query, appstruct):
        debit = appstruct.get("debit", {})
        if debit.get("start") not in (None, colander.null):
            logger.info("  + Filtering by debit amount : %s" % debit)
            start = debit.get("start")
            end = debit.get("end")
            if end in (None, colander.null):
                query = query.filter(AccountingOperation.debit >= start)
            else:
                query = query.filter(AccountingOperation.debit.between(start, end))
        return query

    def filter_credit(self, query, appstruct):
        credit = appstruct.get("credit", {})
        if credit.get("start") not in (None, colander.null):
            logger.info("  + Filtering by credit amount : %s" % credit)
            start = credit.get("start")
            end = credit.get("end")
            if end in (None, colander.null):
                query = query.filter(AccountingOperation.credit >= start)
            else:
                query = query.filter(AccountingOperation.credit.between(start, end))
        return query

    # used to get the name of each account number
    def get_wording_dict(self):
        query = GeneralLedgerAccountWording.query().all()
        wording_dict = {}
        for line in query:
            wording_dict[line.account_number] = line.wording
        return wording_dict


class CompanyGeneralLedgerOperationsListView(
    CompanyGeneralLedgerOperationsListTools,
    BaseListView,
):
    """
    View for listing general ledger operations of a company
    """

    add_template_vars = (
        "title",
        "get_wording_dict",
    )


def includeme(config):
    config.add_view(
        CompanyGeneralLedgerOperationsListView,
        route_name=COMPANY_GENERAL_LEDGER_OPERATION,
        renderer="/accounting/general_ledger_operations.mako",
        permission=PERMISSIONS["company.view_accounting"],
    )
    config.add_company_menu(
        parent="accounting",
        order=3,
        label="Grand livre",
        route_name=COMPANY_GENERAL_LEDGER_OPERATION,
        route_id_key="company_id",
    )

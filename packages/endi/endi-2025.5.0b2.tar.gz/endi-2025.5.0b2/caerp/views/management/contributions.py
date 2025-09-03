import datetime
import colander

from caerp.consts.permissions import PERMISSIONS
from sqlalchemy import func

from caerp_base.models.base import DBSESSION
from caerp.export.utils import write_file_to_request
from caerp.export.excel import XlsExporter
from caerp.export.ods import OdsExporter
from caerp.forms.management.contributions import get_list_schema
from caerp.models.accounting.bookeeping import CustomInvoiceBookEntryModule
from caerp.models.accounting.operations import AccountingOperation
from caerp.models.company import Company, CompanyActivity
from caerp.utils.accounting import get_financial_year_data
from caerp.utils.strings import short_month_name
from caerp.views import BaseListView
from caerp.views.admin.sale.accounting.invoice import MODULE_COLLECTION_URL
from caerp.views.admin.sale.accounting.internalinvoice import (
    MODULE_COLLECTION_URL as INTERNAL_MODULE_COLLECTION_URL,
)
from caerp.views.management.utils import get_active_companies_on_period


class ContributionsManagementView(BaseListView):
    """
    Tableau de suivi des contributions
    """

    title = "Suivi des contributions"
    schema = get_list_schema()
    use_paginate = False

    def get_exercice_data(self):
        financial_year = self.appstruct.get("financial_year")
        if financial_year in (None, colander.null):
            financial_year = datetime.date.today().year
        return get_financial_year_data(financial_year)

    def get_period_months(self):
        months = []
        exercice = self.get_exercice_data()
        year = exercice["start_year"]
        month = exercice["start_month"]
        while year != exercice["end_year"] or month != exercice["end_month"]:
            months.append((year, month))
            month = month + 1
            if month > 12:
                month = 1
                year = year + 1
        months.append((exercice["end_year"], exercice["end_month"]))
        return months

    def query(self):
        exercice = self.get_exercice_data()
        return get_active_companies_on_period(
            exercice["start_date"], exercice["end_date"]
        )

    def filter_follower_id(self, query, appstruct):
        follower_id = appstruct.get("follower_id")
        if follower_id not in (None, colander.null):
            if follower_id == -2:
                # -2 means no follower configured
                query = query.filter(Company.follower_id == None)
            else:
                query = query.filter(Company.follower_id == follower_id)
        return query

    def filter_antenne_id(self, query, appstruct):
        antenne_id = appstruct.get("antenne_id")
        if antenne_id not in (None, colander.null):
            if antenne_id == -2:
                # -2 means no antenne configured
                query = query.filter(Company.antenne_id == None)
            else:
                query = query.filter(Company.antenne_id == antenne_id)
        return query

    def filter_activity_id(self, query, appstruct):
        activity_id = appstruct.get("activity_id")
        if activity_id not in (None, colander.null):
            query = query.filter(
                Company.activities.any(CompanyActivity.id == activity_id)
            )
        return query

    def filter_active(self, query, appstruct):
        active_only = appstruct.get("active")
        if active_only not in (None, colander.null, False):
            query = query.filter(Company.active == True)
        return query

    def filter_internal(self, query, appstruct):
        no_internal = appstruct.get("internal")
        if no_internal not in (None, colander.null, False):
            query = query.filter(Company.internal == False)
        return query

    def get_contibutions_accounting_accounts(self):
        """
        Return accounting accounts to use for contribution calculation
        (accounts configured in CustomInvoiceBookEntryModules of type 'contribution')
        """
        contribution_accounts = []
        query = (
            DBSESSION()
            .query(
                CustomInvoiceBookEntryModule.compte_cg_debit,
                CustomInvoiceBookEntryModule.compte_cg_credit,
            )
            .filter(CustomInvoiceBookEntryModule.enabled == 1)
            .filter(CustomInvoiceBookEntryModule.name == "contribution")
            .all()
        )
        for debit_account, credit_account in query:
            if debit_account not in contribution_accounts:
                contribution_accounts.append(debit_account)
            if credit_account not in contribution_accounts:
                contribution_accounts.append(credit_account)
        return contribution_accounts

    def get_contributions_amounts_on_period(self, period_start, period_end):
        """
        Return all contributions amounts by company and month for the given period
        """
        contributions_amounts = {}
        query = (
            DBSESSION()
            .query(
                Company,
                func.left(AccountingOperation.date, 7).label("period"),
                func.extract("YEAR", AccountingOperation.date).label("year"),
                func.extract("MONTH", AccountingOperation.date).label("month"),
                func.sum(AccountingOperation.debit - AccountingOperation.credit).label(
                    "contribution_value"
                ),
            )
            .join(AccountingOperation.company)
            .filter(AccountingOperation.date.between(period_start, period_end))
            .filter(
                AccountingOperation.general_account.in_(
                    self.get_contibutions_accounting_accounts()
                )
            )
            .group_by(
                AccountingOperation.analytical_account,
                func.extract("YEAR", AccountingOperation.date),
                func.extract("MONTH", AccountingOperation.date),
            )
        )

        for company, period, year, month, contribution_value in query.all():
            if not company.id in contributions_amounts:
                contributions_amounts[company.id] = {}
            period = f"{year}-{month}"
            contributions_amounts[company.id][period] = contribution_value

        return contributions_amounts

    def compute_contributions_datas(self, companies, period_start, period_end):
        """
        Return contribution amounts for the given companies for each month of the given period
        """
        contributions_datas = {}
        contributions_amounts = self.get_contributions_amounts_on_period(
            period_start, period_end
        )
        for company in companies:
            contributions_datas[company.id] = []
            for year, month in self.get_period_months():
                month_value = 0
                if company.id in contributions_amounts:
                    if f"{year}-{month}" in contributions_amounts[company.id]:
                        month_value = contributions_amounts[company.id][
                            f"{year}-{month}"
                        ]
                contributions_datas[company.id].append(month_value)

        return contributions_datas

    def compute_aggregate_datas(self, contributions_datas):
        """
        Calcule les totaux à partir des données des enseignes
        """
        contributions_list = []
        for company_id, contributions_values in contributions_datas.items():
            contributions_list.append(contributions_values)
        return [sum(i) for i in zip(*contributions_list)]

    def _build_return_value(self, schema, appstruct, query):
        """
        Return the datas expected by the template
        """
        companies = query
        exercice = self.get_exercice_data()
        contributions_datas = self.compute_contributions_datas(
            companies, exercice["start_date"], exercice["end_date"]
        )

        if schema is not None:
            if self.error is not None:
                form_object = self.error
                form_render = self.error.render()
            else:
                form = self.get_form(schema)
                if appstruct and "__formid__" in self.request.GET:
                    form.set_appstruct(appstruct)
                form_object = form
                form_render = form.render()

        return dict(
            title=self.title,
            form_object=form_object,
            form=form_render,
            exercice=exercice,
            months=self.get_period_months(),
            companies=companies,
            contributions_datas=contributions_datas,
            aggregate_datas=self.compute_aggregate_datas(contributions_datas),
            export_xls_url=self.request.route_path(
                "management_contributions_export",
                extension="xls",
                _query=self.request.GET,
            ),
            export_ods_url=self.request.route_path(
                "management_contributions_export",
                extension="ods",
                _query=self.request.GET,
            ),
            config_modules_url=self.request.route_path(MODULE_COLLECTION_URL),
            config_internal_modules_url=self.request.route_path(
                INTERNAL_MODULE_COLLECTION_URL
            ),
        )


class ContributionsManagementXlsView(ContributionsManagementView):
    """
    Export du tableau de suivi des contributions au format XLSX
    """

    _factory = XlsExporter

    @property
    def filename(self):
        exercice = self.get_exercice_data()
        return "suivi_contributions_{}.{}".format(
            exercice["label"],
            self.request.matchdict["extension"],
        )

    def _build_return_value(self, schema, appstruct, query):
        writer = self._factory()
        writer._datas = []
        # Récupération des données
        companies = query
        exercice = self.get_exercice_data()
        contributions_datas = self.compute_contributions_datas(
            companies, exercice["start_date"], exercice["end_date"]
        )
        aggregate_datas = self.compute_aggregate_datas(contributions_datas)
        # En-têtes
        headers = [
            "Enseigne",
        ]
        for year, month in self.get_period_months():
            headers.append(f"{short_month_name(month)} {str(year)[2:]}")
        headers.append("TOTAL")
        writer.add_headers(headers)
        # Données des contributions
        for company in companies:
            row_data = [
                company.name,
            ]
            for month_value in contributions_datas[company.id]:
                row_data.append(month_value)
            row_data.append(sum(contributions_datas[company.id]))
            writer.add_row(row_data)
        # Total
        row_total = [
            "TOTAL",
        ]
        for month_value in aggregate_datas:
            row_total.append(month_value)
        row_total.append(sum(aggregate_datas))
        writer.add_row(row_total, options={"highlighted": True})
        # Génération du fichier d'export
        write_file_to_request(self.request, self.filename, writer.render())
        return self.request.response


class ContributionsManagementOdsView(ContributionsManagementXlsView):
    """
    Export du tableau de suivi des contributions au format ODS
    """

    _factory = OdsExporter


def includeme(config):
    config.add_route(
        "management_contributions",
        "management/contributions",
    )
    config.add_route(
        "management_contributions_export", "management/contributions.{extension}"
    )
    config.add_view(
        ContributionsManagementView,
        route_name="management_contributions",
        renderer="management/contributions.mako",
        permission=PERMISSIONS["global.company_view_accounting"],
    )
    config.add_view(
        ContributionsManagementXlsView,
        route_name="management_contributions_export",
        match_param="extension=xls",
        permission=PERMISSIONS["global.company_view_accounting"],
    )
    config.add_view(
        ContributionsManagementOdsView,
        route_name="management_contributions_export",
        match_param="extension=ods",
        permission=PERMISSIONS["global.company_view_accounting"],
    )
    config.add_admin_menu(
        parent="management",
        order=0,
        label="Contributions",
        href="/management/contributions",
    )

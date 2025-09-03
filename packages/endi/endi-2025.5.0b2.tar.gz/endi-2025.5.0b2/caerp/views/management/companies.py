import datetime
import colander

from caerp.consts.permissions import PERMISSIONS
from caerp.export.utils import write_file_to_request
from caerp.export.excel import XlsExporter
from caerp.export.ods import OdsExporter
from caerp.forms.management.companies import get_list_schema
from caerp.models.company import Company, CompanyActivity
from caerp.utils.accounting import get_financial_year_data
from caerp.views import BaseListView
from caerp.views.management.utils import (
    compute_diff_percent,
    get_active_companies_on_period,
)


class CompaniesManagementView(BaseListView):
    """
    Tableau de suivi des enseignes
    """

    title = "Suivi des enseignes de la CAE"
    schema = get_list_schema()
    use_paginate = False

    def get_exercice_data(self, previous=False):
        financial_year = self.appstruct.get("financial_year")
        if financial_year in (None, colander.null):
            financial_year = datetime.date.today().year
        if previous:
            financial_year -= 1
        return get_financial_year_data(financial_year)

    def query(self):
        current_exercice = self.get_exercice_data()
        previous_exercice = self.get_exercice_data(previous=True)
        return get_active_companies_on_period(
            previous_exercice["start_date"], current_exercice["end_date"]
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

    def compute_companies_datas(self, companies, current_exercice, previous_exercice):
        """
        Calcule les indicateurs de suivi pour chaque enseigne
        sur l'exercice en cours et le précédent
        """
        companies_datas = []
        for company in companies:
            # Chiffres d'affaire
            current_turnover = company.get_turnover(
                current_exercice["start_date"], current_exercice["end_date"]
            )
            previous_turnover = company.get_turnover(
                previous_exercice["start_date"], previous_exercice["end_date"]
            )
            turnover_diff = compute_diff_percent(current_turnover, previous_turnover)
            # Dépenses + kilomètres
            current_expenses, current_kms = company.get_total_expenses_and_km_on_period(
                current_exercice["start_date"], current_exercice["end_date"]
            )
            (
                previous_expenses,
                previous_kms,
            ) = company.get_total_expenses_and_km_on_period(
                previous_exercice["start_date"], previous_exercice["end_date"]
            )
            # Achats
            current_purchases = company.get_total_purchases_on_period(
                current_exercice["start_date"], current_exercice["end_date"]
            )
            previous_purchases = company.get_total_purchases_on_period(
                previous_exercice["start_date"], previous_exercice["end_date"]
            )
            # Tréso
            treasury_datas = company.get_last_treasury_main_indicator()
            # Ajout des données de l'enseigne au tableau général
            companies_datas.append(
                {
                    "company": company,
                    "current_turnover": current_turnover,
                    "previous_turnover": previous_turnover,
                    "turnover_diff": turnover_diff,
                    "current_expenses": current_expenses,
                    "previous_expenses": previous_expenses,
                    "current_purchases": current_purchases,
                    "previous_purchases": previous_purchases,
                    "current_kms": current_kms,
                    "previous_kms": previous_kms,
                    "treasury_datas": treasury_datas,
                }
            )
        return companies_datas

    def compute_aggregate_datas(self, companies_datas):
        """
        Calcule les totaux à partir des données des enseignes
        """
        aggregate_datas = {
            "current_turnover": 0,
            "previous_turnover": 0,
            "turnover_diff": 0,
            "current_expenses": 0,
            "previous_expenses": 0,
            "current_purchases": 0,
            "previous_purchases": 0,
            "current_kms": 0,
            "previous_kms": 0,
        }
        for data in companies_datas:
            aggregate_datas["current_turnover"] += data["current_turnover"]
            aggregate_datas["previous_turnover"] += data["previous_turnover"]
            aggregate_datas["current_expenses"] += data["current_expenses"]
            aggregate_datas["previous_expenses"] += data["previous_expenses"]
            aggregate_datas["current_purchases"] += data["current_purchases"]
            aggregate_datas["previous_purchases"] += data["previous_purchases"]
            aggregate_datas["current_kms"] += data["current_kms"]
            aggregate_datas["previous_kms"] += data["previous_kms"]

        aggregate_datas["turnover_diff"] = compute_diff_percent(
            aggregate_datas["current_turnover"],
            aggregate_datas["previous_turnover"],
        )
        return aggregate_datas

    def _build_return_value(self, schema, appstruct, query):
        """
        Return the datas expected by the template
        """
        current_exercice = self.get_exercice_data()
        previous_exercice = self.get_exercice_data(previous=True)
        companies = query
        companies_datas = self.compute_companies_datas(
            companies, current_exercice, previous_exercice
        )
        aggregate_datas = self.compute_aggregate_datas(companies_datas)

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
            current_exercice=current_exercice,
            previous_exercice=previous_exercice,
            nb_companies=companies.count(),
            companies_datas=companies_datas,
            aggregate_datas=aggregate_datas,
            export_xls_url=self.request.route_path(
                "management_companies_export",
                extension="xls",
                _query=self.request.GET,
            ),
            export_ods_url=self.request.route_path(
                "management_companies_export",
                extension="ods",
                _query=self.request.GET,
            ),
        )


class CompaniesManagementXlsView(CompaniesManagementView):
    """
    Export du tableau de suivi des enseignes au format XLSX
    """

    _factory = XlsExporter

    @property
    def filename(self):
        return "suivi_enseignes_{}.{}".format(
            datetime.date.today().strftime("%Y-%m-%d"),
            self.request.matchdict["extension"],
        )

    def _build_return_value(self, schema, appstruct, query):
        writer = self._factory()
        writer._datas = []
        # Récupération des données
        current_exercice = self.get_exercice_data()
        previous_exercice = self.get_exercice_data(previous=True)
        companies = query
        companies_datas = self.compute_companies_datas(
            companies, current_exercice, previous_exercice
        )
        aggregate_datas = self.compute_aggregate_datas(companies_datas)
        # En-têtes
        headers = [
            "Enseigne",
            "Activité principale",
            "Active",
            "CA {}".format(current_exercice["label"]),
            "CA {}".format(previous_exercice["label"]),
            "Écart",
            "Dépenses {}".format(current_exercice["label"]),
            "Dépenses {}".format(previous_exercice["label"]),
            "Achats {}".format(current_exercice["label"]),
            "Achats {}".format(previous_exercice["label"]),
            "TOTAL {}".format(current_exercice["label"]),
            "TOTAL {}".format(previous_exercice["label"]),
            "Nb Km {}".format(current_exercice["label"]),
            "Nb Km {}".format(previous_exercice["label"]),
            "Trésorerie",
        ]
        writer.add_headers(headers)
        # Données des enseignes
        for data in companies_datas:
            row_data = [
                data["company"].name,
                data["company"].main_activity,
                data["company"].active,
                data["current_turnover"],
                data["previous_turnover"],
                data["turnover_diff"],
                data["current_expenses"],
                data["previous_expenses"],
                data["current_purchases"],
                data["previous_purchases"],
                data["current_turnover"]
                - data["current_expenses"]
                - data["current_purchases"],
                data["previous_turnover"]
                - data["previous_expenses"]
                - data["previous_purchases"],
                data["current_kms"] / 100,
                data["previous_kms"] / 100,
            ]
            if data["treasury_datas"] is not None:
                row_data.append(data["treasury_datas"]["value"])
            writer.add_row(row_data)
        # Total
        row_total = [
            "TOTAL",
            "",
            "",
            aggregate_datas["current_turnover"],
            aggregate_datas["previous_turnover"],
            aggregate_datas["turnover_diff"],
            aggregate_datas["current_expenses"],
            aggregate_datas["previous_expenses"],
            aggregate_datas["current_purchases"],
            aggregate_datas["previous_purchases"],
            aggregate_datas["current_turnover"]
            - aggregate_datas["current_expenses"]
            - aggregate_datas["current_purchases"],
            aggregate_datas["previous_turnover"]
            - aggregate_datas["previous_expenses"]
            - aggregate_datas["previous_purchases"],
            aggregate_datas["current_kms"] / 100,
            aggregate_datas["previous_kms"] / 100,
            "",
        ]
        writer.add_row(row_total, options={"highlighted": True})
        # Génération du fichier d'export
        write_file_to_request(self.request, self.filename, writer.render())
        return self.request.response


class CompaniesManagementOdsView(CompaniesManagementXlsView):
    """
    Export du tableau de suivi des enseignes au format ODS
    """

    _factory = OdsExporter


def includeme(config):
    config.add_route(
        "management_companies",
        "management/companies",
    )
    config.add_route("management_companies_export", "management/companies.{extension}")
    config.add_view(
        CompaniesManagementView,
        route_name="management_companies",
        renderer="management/companies.mako",
        permission=PERMISSIONS["global.company_view_accounting"],
    )
    config.add_view(
        CompaniesManagementXlsView,
        route_name="management_companies_export",
        match_param="extension=xls",
        permission=PERMISSIONS["global.company_view_accounting"],
    )
    config.add_view(
        CompaniesManagementOdsView,
        route_name="management_companies_export",
        match_param="extension=ods",
        permission=PERMISSIONS["global.company_view_accounting"],
    )
    config.add_admin_menu(
        parent="management",
        order=0,
        label="Enseignes",
        href="/management/companies",
        permission=PERMISSIONS["global.company_view_accounting"],
    )

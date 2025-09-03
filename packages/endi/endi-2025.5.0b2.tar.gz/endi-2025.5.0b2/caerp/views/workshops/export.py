import colander
from caerp.consts.permissions import PERMISSIONS
from sqlalchemy import (
    or_,
)
from sqla_inspect.csv import CsvExporter
from sqla_inspect.excel import XlsExporter
from sqla_inspect.ods import OdsExporter

from caerp.models.company import Company
from caerp.models.user.user import User
from caerp.models.workshop import Workshop
from caerp.views import BaseCsvView
from caerp.views.workshops.lists import WorkshopListTools
from caerp.views.render_api import format_account


class WorkshopCsvWriter(CsvExporter):
    headers = (
        {"name": "date", "label": "Date"},
        {"name": "label", "label": "Intitulé"},
        {"name": "name", "label": "Nom"},
        {"name": "role", "label": "Rôle"},
        {"name": "duration", "label": "Durée"},
        {"name": "attended", "label": "Participation"},
        {"name": "info1", "label": "Action 1"},
        {"name": "info2", "label": "Action 2"},
        {"name": "info3", "label": "Action 3"},
    )


class WorkshopXlsWriter(XlsExporter):
    headers = (
        {"name": "date", "label": "Date"},
        {"name": "label", "label": "Intitulé"},
        {"name": "name", "label": "Nom"},
        {"name": "role", "label": "Rôle"},
        {"name": "duration", "label": "Durée"},
        {"name": "attended", "label": "Participation"},
        {"name": "info1", "label": "Action 1"},
        {"name": "info2", "label": "Action 2"},
        {"name": "info3", "label": "Action 3"},
    )


class WorkshopOdsWriter(OdsExporter):
    headers = (
        {"name": "date", "label": "Date"},
        {"name": "label", "label": "Intitulé"},
        {"name": "name", "label": "Nom"},
        {"name": "role", "label": "Rôle"},
        {"name": "duration", "label": "Durée"},
        {"name": "attended", "label": "Participation"},
        {"name": "info1", "label": "Action 1"},
        {"name": "info2", "label": "Action 2"},
        {"name": "info3", "label": "Action 3"},
    )


def stream_workshop_entries_for_export(query):
    """
    Stream workshop datas for csv export
    """
    for workshop in query.all():
        hours = sum(t.duration[0] for t in workshop.timeslots)
        minutes = sum(t.duration[1] for t in workshop.timeslots)

        duration = hours * 60 + minutes

        start_date = workshop.timeslots[0].start_time.date()

        (info1, info2, info3) = map(
            lambda info: None if info is None else info.label,
            [workshop.info1, workshop.info2, workshop.info3],
        )

        for participant in workshop.participants:
            attended = False
            for timeslot in workshop.timeslots:
                if timeslot.user_status(participant.id) == "Présent":
                    attended = True
                    break

            yield {
                "date": start_date,
                "label": workshop.name,
                "name": format_account(participant),
                "role": "apprenant",
                "duration": duration,
                "attended": "Oui" if attended else "Non",
                "info1": info1,
                "info2": info2,
                "info3": info3,
            }

        for trainer in workshop.trainers:
            yield {
                "date": start_date,
                "label": workshop.name,
                "name": format_account(trainer),
                "role": "formateur",
                "duration": duration,
                "info1": info1,
                "info2": info2,
                "info3": info3,
            }


class WorkshopCsvView(WorkshopListTools, BaseCsvView):
    """
    Workshop csv export view
    """

    writer = WorkshopCsvWriter

    @property
    def filename(self):
        return "ateliers.csv"

    def _init_writer(self):
        return self.writer()

    def _stream_rows(self, query):
        return stream_workshop_entries_for_export(query)


class CaeWorkshopCsvView(WorkshopCsvView):
    """
    cae Workshop csv export view
    """

    def filter_company_manager_or_cae(self, query, appstruct):
        company_manager = appstruct.get("company_manager")
        if company_manager == colander.null:
            query = query.filter(Workshop.company_manager_id == None)  # noqa: E711
        elif company_manager is not None:
            if company_manager in (-1, "-1"):
                query = query.outerjoin(Workshop.company_manager).filter(
                    or_(
                        Workshop.company_manager_id == None,  # noqa: E711
                        Company.internal == True,
                    )
                )
            else:
                query = query.filter(
                    Workshop.company_manager_id == int(company_manager)
                )
        return query


class CompanyWorkshopCsvView(WorkshopCsvView):
    """
    company Workshop csv export view
    """

    def filter_company_manager_or_cae(self, query, appstruct):
        company = self.context
        employee_ids = company.get_employee_ids()
        query = query.filter(
            or_(
                Workshop.company_manager_id == company.id,
                Workshop.trainers.any(User.id.in_(employee_ids)),
            )
        )
        return query


class WorkshopXlsView(WorkshopCsvView):
    """
    Workshop excel export view
    """

    writer = WorkshopXlsWriter

    @property
    def filename(self):
        return "ateliers.xlsx"


class CaeWorkshopXlsView(WorkshopXlsView):
    """
    cae Workshop xlsx export view
    """

    def filter_company_manager_or_cae(self, query, appstruct):
        company_manager = appstruct.get("company_manager")
        if company_manager == colander.null:
            query = query.filter(Workshop.company_manager_id == None)  # noqa: E711
        elif company_manager is not None:
            if company_manager in (-1, "-1"):
                query = query.outerjoin(Workshop.company_manager).filter(
                    or_(
                        Workshop.company_manager_id == None,  # noqa: E711
                        Company.internal == True,
                    )
                )
            else:
                query = query.filter(
                    Workshop.company_manager_id == int(company_manager)
                )
        return query


class CompanyWorkshopXlsView(WorkshopXlsView):
    """
    company Workshop xlsx export view
    """

    def filter_company_manager_or_cae(self, query, appstruct):
        company = self.context
        employee_ids = company.get_employee_ids()
        query = query.filter(
            or_(
                Workshop.company_manager_id == company.id,
                Workshop.trainers.any(User.id.in_(employee_ids)),
            )
        )
        return query


class WorkshopOdsView(WorkshopCsvView):
    """
    Workshop ods export view
    """

    writer = WorkshopOdsWriter

    @property
    def filename(self):
        return "ateliers.ods"


class CaeWorkshopOdsView(WorkshopOdsView):
    """
    cae Workshop ods export view
    """

    def filter_company_manager_or_cae(self, query, appstruct):
        company_manager = appstruct.get("company_manager")
        if company_manager == colander.null:
            query = query.filter(Workshop.company_manager_id == None)  # noqa: E711
        elif company_manager is not None:
            if company_manager in (-1, "-1"):
                query = query.outerjoin(Workshop.company_manager).filter(
                    or_(
                        Workshop.company_manager_id == None,  # noqa: E711
                        Company.internal == True,
                    )
                )
            else:
                query = query.filter(
                    Workshop.company_manager_id == int(company_manager)
                )
        return query


class CompanyWorkshopOdsView(WorkshopOdsView):
    """
    company Workshop ods export view
    """

    def filter_company_manager_or_cae(self, query, appstruct):
        company = self.context
        employee_ids = company.get_employee_ids()
        query = query.filter(
            or_(
                Workshop.company_manager_id == company.id,
                Workshop.trainers.any(User.id.in_(employee_ids)),
            )
        )
        return query


def includeme(config):
    # View EA
    config.add_view(
        WorkshopCsvView,
        route_name="workshops{file_format}",
        match_param="file_format=.csv",
        permission=PERMISSIONS["global.manage_workshop"],
    )

    config.add_view(
        CaeWorkshopCsvView,
        route_name="cae_workshops{file_format}",
        match_param="file_format=.csv",
        permission=PERMISSIONS["global.manage_workshop"],
    )

    config.add_view(
        WorkshopXlsView,
        route_name="workshops{file_format}",
        match_param="file_format=.xlsx",
        permission=PERMISSIONS["global.manage_workshop"],
    )

    config.add_view(
        CaeWorkshopXlsView,
        route_name="cae_workshops{file_format}",
        match_param="file_format=.xlsx",
        permission=PERMISSIONS["global.manage_workshop"],
    )
    config.add_view(
        WorkshopOdsView,
        route_name="workshops{file_format}",
        match_param="file_format=.ods",
        permission=PERMISSIONS["global.manage_workshop"],
    )

    config.add_view(
        CaeWorkshopOdsView,
        route_name="cae_workshops{file_format}",
        match_param="file_format=.ods",
        permission=PERMISSIONS["global.manage_workshop"],
    )

    # View ES
    config.add_view(
        CompanyWorkshopCsvView,
        route_name="company_workshops{file_format}",
        match_param="file_format=.csv",
        context=Company,
        permission=PERMISSIONS["company.view"],
    )

    config.add_view(
        CompanyWorkshopXlsView,
        route_name="company_workshops{file_format}",
        match_param="file_format=.xlsx",
        context=Company,
        permission=PERMISSIONS["company.view"],
    )

    config.add_view(
        CompanyWorkshopOdsView,
        route_name="company_workshops{file_format}",
        match_param="file_format=.ods",
        permission=PERMISSIONS["company.view"],
    )

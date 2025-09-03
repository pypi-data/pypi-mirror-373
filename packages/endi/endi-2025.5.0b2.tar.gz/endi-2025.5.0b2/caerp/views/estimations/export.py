import logging

from caerp_celery.models import FileGenerationJob
from caerp_celery.tasks.export import export_estimations_details_to_file, export_to_file
from sqlalchemy.orm import load_only

from caerp.consts.permissions import PERMISSIONS
from caerp.models.company import Company
from caerp.models.task import Estimation, Task
from caerp.views import AsyncJobMixin, BaseListView

from .lists import GlobalEstimationListTools

logger = log = logging.getLogger(__name__)


class GlobalEstimationsCsvView(
    AsyncJobMixin,
    GlobalEstimationListTools,
    BaseListView,
):
    model = Estimation
    file_format = "csv"
    filename = "devis_"

    def query(self):
        query = self.request.dbsession.query(Estimation)
        query = query.outerjoin(Task.company)
        query = query.outerjoin(Task.customer)
        query = query.options(load_only(Task.id))
        return query

    def _get_company_id(self, appstruct):
        return appstruct.get("company_id")

    def _build_return_value(self, schema, appstruct, query):
        """
        Return the streamed file object
        """
        all_ids = [elem.id for elem in query]
        logger.debug("    + All_ids where collected : {0}".format(all_ids))
        if not all_ids:
            return self.show_error("Aucune facture ne correspond à cette requête")

        celery_error_resp = self.is_celery_alive()
        if celery_error_resp:
            return celery_error_resp
        else:
            logger.debug("    + In the GlobalEstimationsCsvView._build_return_value")
            job_result = self.initialize_job_result(FileGenerationJob)

            logger.debug("    + Delaying the export_to_file task")
            celery_job = export_to_file.delay(
                job_result.id, "estimations", all_ids, self.filename, self.file_format
            )
            return self.redirect_to_job_watch(celery_job, job_result)


def filter_all_status(self, query, appstruct):
    """
    Filter the estimation by status
    """
    status = appstruct.get("status", "all")
    if status != "all":
        logger.info("  + Status filtering : %s" % status)
        query = query.filter(Task.status == status)

    return query


class GlobalEstimationsXlsView(GlobalEstimationsCsvView):
    file_format = "xls"


class GlobalEstimationsOdsView(GlobalEstimationsCsvView):
    file_format = "ods"


class CompanyEstimationsCsvView(GlobalEstimationsCsvView):
    is_global = False
    excluded_fields = ("company_id",)

    def _get_company_id(self, appstruct):
        return self.request.context.id

    filter_status = filter_all_status


class CompanyEstimationsXlsView(CompanyEstimationsCsvView):
    file_format = "xls"


class CompanyEstimationsOdsView(CompanyEstimationsCsvView):
    file_format = "ods"


class GlobalEstimationsDetailsCsvView(
    AsyncJobMixin,
    GlobalEstimationListTools,
    BaseListView,
):
    file_format = "csv"

    def query(self):
        query = self.request.dbsession.query(Task)
        query = query.with_polymorphic([Estimation])
        query = query.outerjoin(Task.customer)
        query = query.outerjoin(Task.company)
        query = query.options(load_only(Task.id))
        return query

    def _get_company_id(self, appstruct):
        return appstruct.get("company_id")

    def _build_return_value(self, schema, appstruct, query):
        """
        Return the streamed file object
        """
        task_ids = [elem.id for elem in query]
        logger.debug("    + Estimations ids where collected : {0}".format(task_ids))
        if not task_ids:
            return self.show_error("Aucune facture ne correspond à cette requête")

        celery_error_resp = self.is_celery_alive()
        if celery_error_resp:
            return celery_error_resp
        else:
            logger.debug(
                "    + In the GlobalEstimationsDetailsCsvView._build_return_value"
            )
            job_result = self.initialize_job_result(FileGenerationJob)

            logger.debug("    + Delaying the export_estimations_details_to_file task")
            celery_job = export_estimations_details_to_file.delay(
                job_result.id,
                task_ids,
                self.file_format,
            )
            return self.redirect_to_job_watch(celery_job, job_result)


class GlobalEstimationsDetailsXlsView(GlobalEstimationsDetailsCsvView):
    file_format = "xls"


class GlobalEstimationsDetailsOdsView(GlobalEstimationsDetailsCsvView):
    file_format = "ods"


class CompanyEstimationsDetailsCsvView(GlobalEstimationsDetailsCsvView):
    is_global = False
    excluded_fields = ("company_id",)

    def _get_company_id(self, appstruct):
        return self.request.context.id

    filter_status = filter_all_status


class CompanyEstimationsDetailsXlsView(CompanyEstimationsDetailsCsvView):
    file_format = "xls"


class CompanyEstimationsDetailsOdsView(CompanyEstimationsDetailsCsvView):
    file_format = "ods"


def includeme(config):
    """
    Add module's related route
    """

    # Admin  views
    config.add_view(
        GlobalEstimationsCsvView,
        route_name="estimations_export",
        match_param="extension=csv",
        permission=PERMISSIONS["global.list_estimations"],
    )
    config.add_view(
        GlobalEstimationsOdsView,
        route_name="estimations_export",
        match_param="extension=ods",
        permission=PERMISSIONS["global.list_estimations"],
    )
    config.add_view(
        GlobalEstimationsXlsView,
        route_name="estimations_export",
        match_param="extension=xls",
        permission=PERMISSIONS["global.list_estimations"],
    )
    config.add_view(
        GlobalEstimationsDetailsCsvView,
        route_name="estimations_details_export",
        match_param="extension=csv",
        permission=PERMISSIONS["global.list_estimations"],
    )
    config.add_view(
        GlobalEstimationsDetailsOdsView,
        route_name="estimations_details_export",
        match_param="extension=ods",
        permission=PERMISSIONS["global.list_estimations"],
    )
    config.add_view(
        GlobalEstimationsDetailsXlsView,
        route_name="estimations_details_export",
        match_param="extension=xls",
        permission=PERMISSIONS["global.list_estimations"],
    )

    # Company Views
    config.add_view(
        CompanyEstimationsCsvView,
        route_name="company_estimations_export",
        match_param="extension=csv",
        permission=PERMISSIONS["company.view"],
        context=Company,
    )
    config.add_view(
        CompanyEstimationsOdsView,
        route_name="company_estimations_export",
        match_param="extension=ods",
        permission=PERMISSIONS["company.view"],
        context=Company,
    )
    config.add_view(
        CompanyEstimationsXlsView,
        route_name="company_estimations_export",
        match_param="extension=xls",
        permission=PERMISSIONS["company.view"],
        context=Company,
    )
    config.add_view(
        CompanyEstimationsDetailsCsvView,
        route_name="company_estimations_details_export",
        match_param="extension=csv",
        permission=PERMISSIONS["company.view"],
        context=Company,
    )
    config.add_view(
        CompanyEstimationsDetailsOdsView,
        route_name="company_estimations_details_export",
        match_param="extension=ods",
        permission=PERMISSIONS["company.view"],
        context=Company,
    )
    config.add_view(
        CompanyEstimationsDetailsXlsView,
        route_name="company_estimations_details_export",
        match_param="extension=xls",
        permission=PERMISSIONS["company.view"],
        context=Company,
    )

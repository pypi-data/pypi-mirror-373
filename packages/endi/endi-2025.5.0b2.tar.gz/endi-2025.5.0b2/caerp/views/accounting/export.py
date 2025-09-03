from sqla_inspect.csv import CsvExporter
from sqla_inspect.excel import XlsExporter
from sqla_inspect.ods import OdsExporter

from caerp_celery.models import FileGenerationJob
from caerp_celery.tasks.export import export_to_file

from caerp.consts.permissions import PERMISSIONS
from caerp.views import BaseCsvView, BaseView, AsyncJobMixin
from caerp.views.accounting.company_general_ledger import (
    CompanyGeneralLedgerOperationsListTools,
)

from caerp.views.accounting.operations import (
    OperationListTools,
)


def create_company_general_ledger_operations_view(exporter_class, extension):
    class Writer(exporter_class):
        headers = (
            {"name": "general_account_number", "label": "Compte comptable"},
            {"name": "general_account_name", "label": "Nom du compte"},
            {"name": "date", "label": "Date"},
            {"name": "label", "label": "Libellé"},
            {"name": "debit", "label": "Debit"},
            {"name": "credit", "label": "Crédit"},
            {"name": "balance", "label": "Solde"},
        )

    class ExportView(CompanyGeneralLedgerOperationsListTools, BaseCsvView):
        writer = Writer
        filename = "grand-livre.{extension}".format(extension=extension)

        def _init_writer(self):
            return self.writer()

        def _stream_rows(self, query):
            wording = self.get_wording_dict()

            for operation in query.all():
                yield {
                    "general_account_number": operation.general_account,
                    "general_account_name": wording.get(operation.general_account, ""),
                    "label": operation.label,
                    "date": operation.date,
                    "debit": operation.debit,
                    "credit": operation.credit,
                    "balance": operation.balance,
                }

    return ExportView


class ExportAdminOperationsCsvView(OperationListTools, BaseView, AsyncJobMixin):
    extension = "csv"

    def __call__(self):
        all_ids = [op.id for op in self.query()]
        if not all_ids:
            return self.show_error("Aucune écriture ne correspond à cette requête")

        celery_error_resp = self.is_celery_alive()
        if celery_error_resp:
            return celery_error_resp

        if self.context.filetype == "synchronized_accounting":
            period = self.context.date.strftime("%Y")
        else:
            period = self.context.date.strftime("%Y-%m")

        job_result = self.initialize_job_result(FileGenerationJob)
        filename = "ecritures_comptables_{period}.{extension}".format(
            period=period, extension=self.extension
        )
        celery_job = export_to_file.delay(
            job_result.id, "accounting_operations", all_ids, filename, self.extension
        )
        return self.redirect_to_job_watch(celery_job, job_result)


class ExportAdminOperationsXlsView(ExportAdminOperationsCsvView):
    extension = "xlsx"


class ExportAdminOperationsOdsView(ExportAdminOperationsCsvView):
    extension = "ods"


def includeme(config):
    config.add_view(
        create_company_general_ledger_operations_view(CsvExporter, "csv"),
        route_name="grand_livre.{extension}",
        match_param="extension=csv",
        permission=PERMISSIONS["company.view_accounting"],
    )
    config.add_view(
        create_company_general_ledger_operations_view(XlsExporter, "xls"),
        route_name="grand_livre.{extension}",
        match_param="extension=xls",
        permission=PERMISSIONS["company.view_accounting"],
    )
    config.add_view(
        create_company_general_ledger_operations_view(OdsExporter, "ods"),
        route_name="grand_livre.{extension}",
        match_param="extension=ods",
        permission=PERMISSIONS["company.view_accounting"],
    )
    config.add_view(
        ExportAdminOperationsCsvView,
        route_name="operations.{extension}",
        match_param="extension=csv",
        permission=PERMISSIONS["global.manage_accounting"],
    )
    config.add_view(
        ExportAdminOperationsXlsView,
        route_name="operations.{extension}",
        match_param="extension=xls",
        permission=PERMISSIONS["global.manage_accounting"],
    )
    config.add_view(
        ExportAdminOperationsOdsView,
        route_name="operations.{extension}",
        match_param="extension=ods",
        permission=PERMISSIONS["global.manage_accounting"],
    )

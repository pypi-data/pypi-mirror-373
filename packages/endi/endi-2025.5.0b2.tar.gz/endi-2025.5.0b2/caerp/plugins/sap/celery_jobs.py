from caerp.utils.compat import Iterable
import os

from PyPDF4.pdf import PdfFileReader, PdfFileWriter
import transaction
from celery.utils.log import get_task_logger
from caerp_base.models import DBSESSION
from caerp_celery.hacks import setup_rendering_hacks
from pyramid_celery import celery_app

from caerp_celery.models import (
    FileGenerationJob,
    BulkFileGenerationJob,
)
from caerp_celery.tasks import utils
from caerp_celery.tasks.export import (
    GENERATION_ERROR_MESSAGE,
    _get_tmp_directory_path,
    _get_tmp_filepath,
)
from caerp.models.files import File
from caerp.plugins.sap.models.sap import SAPAttestation


class EmptyResult(Exception):
    pass


@celery_app.task(bind=True)
def merge_pdf_files(self, job_id: int, ids: Iterable[int], filename: str):
    """
    Merge several PDF files into one

    :param job_id: FileGenerationJob.id to receive the result
    :param ids: the File.id to be merged and exported
    :param filename: wanted filename (it will receive an id before extension)
    """
    logger = get_task_logger(__name__)
    logger.info("Merging PDF")
    logger.info(" + File ids : %s", ids)

    # Mark job started
    utils.start_job(self.request, FileGenerationJob, job_id)

    # Execute actions
    try:
        base, extension = filename.rsplit(".", 1)
        tmpdir = _get_tmp_directory_path()
        result_filepath = _get_tmp_filepath(tmpdir, base, extension)
        result_filename = os.path.basename(result_filepath)

        files_query = File.query().filter(File.id.in_(ids))

        writer = PdfFileWriter()
        with open(result_filepath, "wb") as fd:
            for file in files_query:
                reader = PdfFileReader(file.data_obj)
                num_of_pages = reader.getNumPages()
                for page in range(num_of_pages):
                    writer.addPage(reader.getPage(page))
            writer.write(fd)
        logger.debug(" -> The file %s been written", result_filepath)

        transaction.commit()
    except:  # noqa
        transaction.abort()
        logger.exception("Error while generating file")
        errors = [GENERATION_ERROR_MESSAGE % job_id]
        utils.record_failure(FileGenerationJob, job_id, errors)
    else:
        utils.record_completed(FileGenerationJob, job_id, filename=result_filename)

    return ""


@celery_app.task(bind=True)
def generate_attestations(
    self,
    job_id: int,
    companies_ids: Iterable[int],
    customers_ids: Iterable[int],
    regenerate_existing: bool,
    year: int,
):
    request = celery_app.conf["PYRAMID_REQUEST"]
    # Ensure layout_manager
    setup_rendering_hacks(request, None)

    logger = get_task_logger(__name__)
    logger.info(
        f"Generating SAP attestations for {year} (restricted to "
        f"companies={len(companies_ids)} and customers={len(customers_ids)})"
    )
    # Mark job started
    utils.start_job(self.request, BulkFileGenerationJob, job_id)

    job_messages = []
    job_errors = []

    # Execute actions
    try:
        results_list = _generate_attestations(
            companies_ids,
            customers_ids,
            job_errors,
            job_messages,
            regenerate_existing,
            request,
            year,
        )

    except:  # noqa
        transaction.abort()
        logger.exception("Error while generating files")
        errors = [GENERATION_ERROR_MESSAGE % job_id]
        utils.record_failure(BulkFileGenerationJob, job_id, errors)
    else:
        transaction.commit()
        utils.record_completed(
            BulkFileGenerationJob,
            job_id,
            results_list=results_list,
            messages=job_messages,
            error_messages=job_errors,
        )
    finally:
        for msg in job_errors:
            logger.error(msg)


def _generate_attestations(
    companies_ids,
    customers_ids,
    job_errors,
    job_messages,
    regenerate_existing,
    request,
    year,
):
    service = SAPAttestation
    out, rejects = service.generate_bulk(
        companies_ids,
        customers_ids,
        regenerate_existing,
        year,
        request,
    )
    out = list(out)
    results_list = [
        dict(
            name=str(attestation),
            regenerated=regenerated,
        )
        for attestation, regenerated in out
    ]
    for reject in rejects:
        msg = str(reject)
        job_errors.append(str(reject))

    attestations_count = len(out)
    overwritten_count = sum(overwritten for obj, overwritten in out)
    if attestations_count > 0:
        if attestations_count == overwritten_count:
            msg = f"{attestations_count} attestations régénérées."
        elif overwritten_count > 0:
            msg = (
                f"{attestations_count} attestations générées"
                f" (dont {overwritten_count} régénérées)."
            )
        else:
            msg = f"{attestations_count} attestations générées."
        job_messages.append(msg)
    else:
        job_errors.append("Aucune attestation à générer avec ces critères.")

    DBSESSION().flush()

    return results_list

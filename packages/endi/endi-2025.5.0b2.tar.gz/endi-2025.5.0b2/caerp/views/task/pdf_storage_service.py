"""
Pdf storage service implementation (interface ITaskPdfStorageService)
"""

import io
import hashlib
import logging

from PyPDF4 import PdfFileMerger

from caerp.interfaces import ISignPDFService
from caerp.export.task_pdf import (
    task_bulk_pdf,
    task_pdf,
)
from caerp.models.files import File
from caerp.views.files.controller import (
    FileData,
    get_filedata_from_file_object_and_stream,
)


logger = logging.getLogger(__name__)


class PdfFileDepotStorageService:
    """
    This class implements the
    :class:`caerp.interfaces.ITaskPdfStorageService`
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request
        if context is None:
            self.context = request.context

    def _get_file_size(self, file_pointer) -> int:
        file_pointer.seek(0)
        size = len(file_pointer.read())
        file_pointer.seek(0)
        return size

    def _get_file_datas(self, file_pointer) -> dict:
        file_pointer.seek(0)
        file_datas = file_pointer.read()
        file_pointer.seek(0)
        return file_datas

    def _sign_pdf(self, filedata_obj: FileData) -> FileData:
        """
        Sign the generated PDF file (with no timestamp) if configurated

        Return the FileData object itself, signed or not
        """
        try:
            pdf_sign_service = self.request.find_service(ISignPDFService)
        except:
            logger.info("No PDF signing service (ISignPDFService) configured")
            pdf_sign_service = None
        if pdf_sign_service:
            filedata_obj.is_signed = pdf_sign_service.sign(
                filedata_obj,
                node_id=self.context.id,
                with_stamp=False,
            )
        return filedata_obj

    def store_pdf(self, filename, pdf_buffer):
        """
        Stores the pdf on disk if needed

        :param obj pdf_buffer: instance of :class:`io.BytesIO`
        :param str filename: The name of the pdf file
        """
        if self.context.status == "valid":
            logger.info("Storing PDF data for document {}".format(self.context))
            self.context.pdf_file = File(
                name=filename,
                mimetype="application/pdf",
                size=self._get_file_size(pdf_buffer),
                description="Fichier Pdf généré",
            )
            filedata_obj = get_filedata_from_file_object_and_stream(
                self.context.pdf_file, pdf_buffer
            )
            if self.context.type_ in self.context.invoice_types:
                filedata_obj = self._sign_pdf(filedata_obj)
            self.context.pdf_file.is_signed = filedata_obj.is_signed
            pdf_buffer = filedata_obj.data
            pdf_datas = self._get_file_datas(pdf_buffer)
            self.context.pdf_file.data = pdf_datas
            pdf_hash = hashlib.sha1(pdf_datas).hexdigest()
            logger.info("Associated PDF hash : {}".format(pdf_hash))
            self.context.pdf_file_hash = pdf_hash
            self.request.dbsession.merge(self.context)
        else:
            logger.debug(
                "We don't persist the PDF data : {} status is "
                "not valid".format(self.context)
            )
        return pdf_buffer

    def retrieve_pdf(self):
        """
        Retrieve the pdf and returns it as a data buffer
        """
        logger.debug("Retrieving PDF datas for {}".format(self.context))
        data = None
        if self.context.pdf_file is not None:
            logger.debug(
                "Retrieving a cached PDF with hash : {}".format(
                    self.context.pdf_file_hash
                )
            )
            try:
                data = self.context.pdf_file.data_obj
                if not data:
                    raise IOError()
            except IOError:
                logger.exception(
                    "The file {} is in the database but can't be retrieved "
                    "from disk : Data corruption ?".format(self.context.pdf_file.id)
                )
                data = None
        return data

    def get_bulk_pdf(self, tasks):
        """
        Produce a Large pdf containing the pdf of all given tasks
        Excludes CGV related informations

        :param list tasks: List of Task instances
        :returns: A pdf as a bytes data buffer
        """
        return task_bulk_pdf(tasks, self.request)

    def set_task(self, task):
        """
        Set task (if it's different from the current context)
        """
        self.context = task


# fix tests pdf


class PdfDevStorageService:
    def __init__(self, context, request):
        self.context = context
        self.request = request
        if context is None:
            self.context = request.context

    def store_pdf(self, filename, pdf_buffer):
        return pdf_buffer

    def retrieve_pdf(self):
        return None

    def get_bulk_pdf(self, tasks):
        result = io.BytesIO()
        writer = PdfFileMerger()
        for task in tasks:
            pdf = task_pdf(task, self.request)
            writer.append(pdf)
        writer.write(result)
        return result

    def set_task(self, task):
        self.context = None

import io
import os
import zipfile

from typing import List

from caerp.models.expense.sheet import ExpenseSheet
from caerp.models.files import File
from caerp.models.supply.supplier_invoice import SupplierInvoice


def mk_zip(file_models: List[File]) -> io.BytesIO:
    """
    Zip all given File objects in a single archive
    """
    zip_archive = io.BytesIO()
    with zipfile.ZipFile(zip_archive, "w", zipfile.ZIP_DEFLATED, False) as file_buffer:
        for file_model in file_models:
            file_buffer.writestr(file_model.name, file_model.getvalue())
    zip_archive.seek(0)
    return zip_archive


def mk_receipt_files_zip(
    file_models: List[File],
    with_month_folder: bool = False,
    with_owner_folder: bool = False,
) -> io.BytesIO:
    """
    Zip all given File objects corresponding to expenses or supplier invoices files
    in a single archive with folders by month and owner if needed
    """
    zip_filelist = []
    zip_archive = io.BytesIO()
    with zipfile.ZipFile(zip_archive, "w", zipfile.ZIP_DEFLATED, False) as file_buffer:
        for file_model in file_models:
            file_path = ""
            file_name = file_model.name
            node = file_model.parent
            if isinstance(node, ExpenseSheet):
                if with_month_folder:
                    file_path += f"{node.year}-{node.month}/"
                if with_owner_folder:
                    file_path += f"{node.user.label}/"
            elif isinstance(node, SupplierInvoice):
                if with_month_folder:
                    file_path += f"{node.date.year}-{node.date.month}/"
                if with_owner_folder:
                    file_path += f"{node.company.name}/"
                file_path += f"{node.remote_invoice_number}/"
            else:
                # Handle only receipts from expense sheets and supplier invoices
                continue
            while f"{file_path}{file_name}" in zip_filelist:
                basename, ext = os.path.splitext(file_name)
                file_name = f"{basename}_1{ext}"
            file_buffer.writestr(f"{file_path}{file_name}", file_model.getvalue())
            zip_filelist.append(f"{file_path}{file_name}")
    zip_archive.seek(0)
    return zip_archive

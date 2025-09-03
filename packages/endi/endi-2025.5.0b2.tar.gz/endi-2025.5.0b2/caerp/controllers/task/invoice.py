from typing import List
from caerp.models.task import Estimation, Invoice

from caerp.services.business import guess_payment_deadline_from_invoice
from caerp.controllers.files import copy_files_from_node


def attach_invoice_to_estimation(request, invoice: Invoice, estimation: Estimation):
    """Attach an invoice to an estimation and handle business related informations"""
    estimation.geninv = True
    invoice.estimation_id = estimation.id
    business = estimation.business
    copy_files_from_node(request, invoice.business, business)
    invoice.business_id = business.id
    guess_payment_deadline_from_invoice(request, business, invoice)
    business.status_service.update_invoicing_status(business, invoice)
    # On supprime l'affaire si nécessaire
    invoice.on_before_commit(request, "delete")

    request.dbsession.merge(estimation)
    request.dbsession.merge(invoice)


def attach_invoices_to_estimation(
    request, estimation: Estimation, invoices: List[Invoice] = None
):
    for invoice in invoices:
        attach_invoice_to_estimation(request, invoice, estimation)

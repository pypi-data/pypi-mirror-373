from caerp.consts.permissions import PERMISSIONS
from caerp.models.task import BaseTaskPayment, Invoice
from caerp.views.payment.invoice import InvoicePaymentRestView
from caerp.views.payment.routes import (
    INVOICE_PAYMENT_API_COLLECTION,
    INVOICE_PAYMENT_API_ITEM_VIEW,
)

from ..forms.tasks.payment import get_sap_payment_schema


class SAPInvoicePaymentRestView(InvoicePaymentRestView):
    def get_schema(self, *args, **kwargs):
        invoice = self._get_invoice()
        return get_sap_payment_schema(self.request, invoice, self.edit)


def includeme(config):
    config.add_rest_view(
        InvoicePaymentRestView,
        collection_context=Invoice,
        collection_route_name=INVOICE_PAYMENT_API_COLLECTION,
        route_name=INVOICE_PAYMENT_API_ITEM_VIEW,
        context=BaseTaskPayment,
        add_rights=PERMISSIONS["context.add_payment_invoice"],
        edit_rights=PERMISSIONS["context.edit_payment"],
        delete_rights=PERMISSIONS["context.delete_payment"],
        view_rights=PERMISSIONS["company.view"],
    )

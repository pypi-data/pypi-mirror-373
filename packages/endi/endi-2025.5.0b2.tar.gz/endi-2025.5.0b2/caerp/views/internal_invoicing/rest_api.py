from caerp.consts.permissions import PERMISSIONS
from caerp.models.task import InternalInvoice

from caerp.views.invoices.rest_api import (
    InvoiceRestView,
    InvoiceStatusRestView,
)


def includeme(config):
    # SAP : Assure que les vues définies pour le SAP n'affectent pas les vues internes
    # Form configuration view
    config.add_view(
        InvoiceRestView,
        attr="form_config",
        route_name="/api/v1/invoices/{id}",
        renderer="json",
        request_param="form_config",
        context=InternalInvoice,
        permission=PERMISSIONS["company.view"],
    )
    # Status View
    config.add_view(
        InvoiceStatusRestView,
        route_name="/api/v1/invoices/{id}",
        request_param="action=status",
        request_method="POST",
        renderer="json",
        context=InternalInvoice,
        permission=PERMISSIONS["context.edit_invoice"],
    )

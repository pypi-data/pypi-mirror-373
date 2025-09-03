"""
Handle Supplier Document related events
"""
import logging

from caerp_base.mail import (
    format_link,
)
from caerp.models.supply.internalsupplier_order import InternalSupplierOrder

from caerp.utils.notification import AbstractNotification, notify

logger = logging.getLogger(__name__)


ORDER_SUBJECT_TMPL = "Votre devis interne {estimation} a été validé par \
{customer}"
ORDER_BODY_TMPL = """\
Bonjour {supplier},

L'enseigne {customer} a émis un bon de commande pour le devis {estimation} \
que vous avez émis.

Vous pouvez consulter votre devis ici :
{url}
"""


def _get_title(node: InternalSupplierOrder) -> str:
    """
    return the subject of the email
    """
    source_estimation = node.source_estimation
    return ORDER_SUBJECT_TMPL.format(
        estimation=source_estimation.name,
        customer=node.company.name,
    )


def _get_body(request, node: InternalSupplierOrder) -> str:
    """
    return the body of the email
    """
    source_estimation = node.source_estimation
    url = request.route_url("/estimations/{id}/general", id=source_estimation.id)
    url = format_link(request.registry.settings, url)
    return ORDER_BODY_TMPL.format(
        supplier=source_estimation.company.name,
        customer=node.company.name,
        url=url,
        estimation=source_estimation.name,
    )


def _get_notification(request, node: InternalSupplierOrder) -> AbstractNotification:
    return AbstractNotification(
        key="supplier_order:status:valid",
        title=_get_title(node),
        body=_get_body(request, node),
    )


def send_supplier_order_validated_mail(request, supplier_order: InternalSupplierOrder):
    """
    Notify the supplier when his customer's order has been validated
    """
    notify(
        request,
        _get_notification(request, supplier_order),
        company_id=supplier_order.source_estimation.company_id,
    )

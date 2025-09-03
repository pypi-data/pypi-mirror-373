"""
Handle Supplier Document related events
"""
import logging
from typing import Union, Optional


from caerp_base.mail import (
    format_link,
)
from caerp.models.supply.supplier_invoice import SupplierInvoice
from caerp.models.supply.supplier_order import SupplierOrder
from caerp.utils.strings import format_status
from caerp.utils.notification import AbstractNotification, notify
from caerp.views.supply.utils import get_supplier_doc_url


logger = logging.getLogger(__name__)

# Events for which a mail will be sended
EVENTS = {
    "valid": "validée",
    "invalid": "invalidée",
    "paid": "partiellement payée",
    "resulted": "payée",
}

SUBJECT_TMPL = "{label} ({supplier}) : {statusstr}"
BODY_TMPL = """\
Bonjour,

{docname} {docnumber} du fournisseur {supplier} {remote_invoice_number}\
a été {status_verb}.

Vous pouvez la consulter ici :
{addr}

Commentaires associés au document :
    {comment}"""


def _get_title(node: Union[SupplierInvoice, SupplierOrder]) -> str:
    """
    return the subject of the email
    """
    if getattr(node, "remote_invoice_number", ""):
        label = f"Facture n°{node.remote_invoice_number}"
    elif node.name:
        label = f"{node.name}"
    elif isinstance(node, SupplierInvoice):
        label = "Facture fournisseur"
    else:
        label = "Commande fournisseur"

    return SUBJECT_TMPL.format(
        label=label,
        supplier=node.supplier.label,
        statusstr=format_status(node),
    )


def _get_status_verb(status: str) -> str:
    """Return the verb associated with the status"""
    return EVENTS.get(status, "")


def _get_body(
    request,
    node: Union[SupplierInvoice, SupplierOrder],
    status: str,
    comment: Optional[str] = None,
) -> str:
    """
    return the body of the email
    """
    status_verb = _get_status_verb(status)

    addr = get_supplier_doc_url(
        request,
        node,
        absolute=True,
    )
    addr = format_link(request.registry.settings, addr)
    if getattr(node, "official_number", None):
        docnumber = node.official_number
    else:
        docnumber = ""
    supplier = node.supplier.label

    if node.type_ == "supplier_invoice":
        docname = "La facture fournisseur"
        remote_invoice_number = f"({node.remote_invoice_number})"
    elif node.type_ == "supplier_order":
        docname = "La commande fournisseur"
        remote_invoice_number = ""
    else:
        return ""

    if not comment:
        if node.status_comment:
            comment = node.status_comment
        else:
            comment = "Aucun"

    return BODY_TMPL.format(
        docname=docname,
        docnumber=docnumber,
        supplier=supplier,
        remote_invoice_number=remote_invoice_number,
        status_verb=status_verb,
        addr=addr,
        comment=comment,
    )


def _get_notification(
    request,
    node: Union[SupplierInvoice, SupplierOrder],
    status: str,
    comment: Optional[str] = None,
) -> AbstractNotification:
    return AbstractNotification(
        key=f"{node.type_}:status:valid",
        title=_get_title(node),
        body=_get_body(request, node, status, comment),
    )


def notify_supplier_document_status_changed(
    request,
    node: Union[SupplierInvoice, SupplierOrder],
    status: str,
    comment: Optional[str] = None,
):
    """Notify end users when supplier document status changed"""
    if status == "paid" and node.paid_status == "resulted":
        status = "resulted"

    if status not in list(EVENTS.keys()):
        return

    notify(
        request,
        _get_notification(request, node, status, comment),
        company_id=node.company_id,
    )

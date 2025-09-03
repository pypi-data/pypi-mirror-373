import logging
import typing
import datetime

from pyramid_mailer.message import Attachment

from caerp_base.mail import (
    format_link,
)

from caerp.models.task.task import Task

from caerp.views.task.utils import get_task_url
from caerp.utils.notification import AbstractNotification, notify
from caerp.utils.strings import (
    format_amount,
    format_status,
    format_account,
)
from caerp.models.files import File


logger = logging.getLogger(__name__)

# Events for which a mail will be sended
EVENTS = {
    "valid": "validé",
    "invalid": "invalidé",
    "paid": "partiellement payé",
    "resulted": "payé",
}

SUBJECT_TMPL = "{docname} ({customer}) : {statusstr}"

MAIL_TMPL = """\
Bonjour {username},

{docname} {docnumber} ({description}) du dossier {project} avec le client {customer} \
a été {status_verb}{gender}.
{more_text}
Vous pouvez {determinant} consulter ici :
{addr}

Commentaires associés au document :
    {comment}"""


def _get_title(task: Task) -> str:
    """
    return the subject of the email
    """
    return SUBJECT_TMPL.format(
        docname=task.name,
        customer=task.customer.label,
        statusstr=format_status(task),
    )


def _get_status_verb(status: str) -> str:
    """
    Return the verb associated to the current status
    """
    return EVENTS.get(status, "")


def _get_payment_date(payment: "Payment") -> datetime.date:
    if isinstance(payment.date, datetime.datetime):
        return payment.date.date()
    else:
        return payment.date


def _find_paid_amount(task: Task) -> int:
    """Collect the amount of the last recorded payment"""
    num_tvas = len(task.get_tvas().keys())
    if num_tvas == 1:
        payment = task.payments[-1]
        amount = payment.amount
    else:
        # Fix #4101 : On a plusieurs tvas dans la facture,
        # on remonte les paiements et on reprend ceux
        # datés du même jour que le dernier et qui ont une tva différente
        last_payment = task.payments[-1]
        amount = last_payment.amount

        for i in range(num_tvas - 1):
            if len(task.payments) <= i + 1:
                break
            # On commence à l'avant dernier paiement et on remonte
            payment = task.payments[-1 * (i + 1) - 1]

            if (
                _get_payment_date(payment) == _get_payment_date(last_payment)
                and payment.tva != last_payment.tva
            ):
                amount += payment.amount
            else:
                break
    return amount


def _get_body(
    request, task: Task, status: str, comment: typing.Optional[str] = None
) -> str:
    """
    return the body of the email
    """
    status_verb = _get_status_verb(status)

    # If the document is validated, we directly send the link to the pdf
    # file
    if status == "valid":
        suffix = ".pdf"
    else:
        suffix = ""

    addr = get_task_url(
        request,
        task,
        suffix=suffix,
        absolute=True,
    )
    addr = format_link(request.registry.settings, addr)
    if task.official_number:
        docnumber = task.official_number
    else:
        docnumber = task.get_short_internal_number()
    customer = task.customer.label
    project = task.project.name.capitalize()
    description = task.name
    if task.type_ == "invoice":
        docname = "La facture"
        gender = "e"
        determinant = "la"
    elif task.type_ == "internalinvoice":
        docname = "La facture interne"
        gender = "e"
        determinant = "la"
    elif task.type_ == "internalcancelinvoice":
        docname = "L'avoir interne"
        gender = ""
        determinant = "le"
    elif task.type_ == "cancelinvoice":
        docname = "L'avoir"
        gender = ""
        determinant = "le"
    elif task.type_ == "estimation":
        docname = "Le devis"
        gender = ""
        determinant = "le"
    elif task.type_ == "internalestimation":
        docname = "Le devis interne"
        gender = ""
        determinant = "le"
    else:
        determinant = ""
        docname = "Inconnu"
        gender = ""

    if status in ["paid", "resulted"] and len(task.payments) > 0:
        amount_in_integer = _find_paid_amount(task)

        amount = format_amount(amount_in_integer, precision=5, grouping=False)
        more_text = f"Un montant de {amount} € a été encaissé."
        if status == "paid":
            topay = task.topay()
            topay = format_amount(topay, precision=5, grouping=False)
            more_text += f"Il reste {topay} € à payer"
    else:
        more_text = "\n"

    if not comment:
        if task.status_comment:
            comment = task.status_comment
        else:
            comment = "Aucun"

    username = format_account(task.owner, reverse=False)
    return MAIL_TMPL.format(
        determinant=determinant,
        username=username,
        docname=docname,
        docnumber=docnumber,
        customer=customer,
        project=project,
        status_verb=status_verb,
        gender=gender,
        addr=addr,
        comment=comment,
        description=description,
        more_text=more_text,
    )


def _get_notification(
    request, task: Task, status: str, comment: typing.Optional[str] = None
) -> AbstractNotification:
    return AbstractNotification(
        key=f"task:status:{status}",
        title=_get_title(task),
        body=_get_body(request, task, status, comment),
    )


def _get_attachment(task: Task) -> typing.Optional[Attachment]:
    """Return the file to be attached to the email"""
    if task.pdf_file:
        file: File = task.pdf_file
        value = file.getvalue()
        if value is not None:
            return Attachment(
                file.name,
                "application/pdf",
                file.getvalue(),
            )


def notify_task_status_changed(
    request, node: Task, status: str, comment: typing.Optional[str] = None
):
    """
    Notify end users when task status changed
    """

    # Silly hack :
    # When a payment is registered, the new status is "paid",
    # if the resulted box has been checked, it's set to resulted later on.
    # So here, we got the paid status, but in reality, the status has
    # already been set to resulted. This hack avoid to send emails with the
    # wrong message
    if status == "paid" and node.paid_status == "resulted":
        status = "resulted"

    if status not in list(EVENTS.keys()):
        return

    attachment = None
    if status == "valid":
        attachment = _get_attachment(node)
    notify(
        request,
        _get_notification(request, node, status, comment),
        company_id=node.company_id,
        attachment=attachment,
    )

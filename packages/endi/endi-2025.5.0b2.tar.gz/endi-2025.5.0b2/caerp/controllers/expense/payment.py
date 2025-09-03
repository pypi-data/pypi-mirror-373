import datetime
import logging
from typing import Optional

from sqlalchemy import select

from caerp.controllers.payment import record_payment
from caerp.controllers.state_managers.payment import check_node_resulted
from caerp.events.document_events import StatusChangedEvent
from caerp.models.expense.payment import ExpensePayment
from caerp.models.expense.sheet import ExpenseSheet
from caerp.models.sepa import ExpenseSepaWaitingPayment
from caerp.models.status import StatusLogEntry
from caerp.utils import strings

logger = logging.getLogger(__name__)


def record_expense_payment(
    request,
    expense_sheet,
    date: datetime.date,
    amount: int,
    mode: str,
    bank_id: int,
    waiver: Optional[bool] = False,
    resulted: Optional[bool] = False,
):
    """
    :param bool resulted: Force the payment to be considered as fully
    covering the ExpenseSheet
    """
    payment = ExpensePayment(
        user_id=request.identity.id,
        date=date,
        amount=amount,
        mode=mode,
        bank_id=bank_id,
        waiver=waiver,
    )
    record_payment(request, expense_sheet, payment)
    check_node_resulted(request, expense_sheet, force_resulted=resulted)

    status_record = StatusLogEntry(
        status=expense_sheet.paid_status,
        user_id=request.identity.id,
        comment="",
        state_manager_key="paid_status",
    )
    expense_sheet.statuses.append(status_record)
    request.dbsession.merge(expense_sheet)
    request.registry.notify(
        StatusChangedEvent(request, expense_sheet, expense_sheet.paid_status)
    )
    return payment


def delete_expense_payment(
    request, expense_sheet: ExpenseSheet, payment: ExpensePayment
):
    logger.info(f"Deleting payment {payment} from expense sheet {expense_sheet}")
    expense_sheet.payments.remove(payment)
    request.dbsession.merge(expense_sheet)
    request.dbsession.flush()
    check_node_resulted(request, expense_sheet, force_resulted=False)
    request.dbsession.merge(expense_sheet)


def create_sepa_waiting_payment(request, expense_sheet: ExpenseSheet, amount):
    """
    Create a waiting payment for the given ExpenseSheet and amount
    """
    assert amount <= expense_sheet.amount_waiting_for_payment() and amount > 0, (
        "Le montant du paiement doit être compris entre 0 et le montant "
        "total de la facture"
    )
    waiting_payment = ExpenseSepaWaitingPayment(
        expense_sheet=expense_sheet, amount=amount
    )
    request.dbsession.add(waiting_payment)
    request.dbsession.flush()
    topay = strings.format_amount(
        waiting_payment.amount, precision=2, html=False, currency=True
    )
    if amount == expense_sheet.total:
        label = f"À payer en totalité : {topay}"
    else:
        label = f"À payer : {topay}"
    log_entry = StatusLogEntry(
        node=expense_sheet,
        state_manager_key="wait_for_payment",
        visibility="management",
        status="valid",
        label=label,
        comment="",
        user=request.identity,
    )
    request.dbsession.add(log_entry)
    request.dbsession.flush()
    return waiting_payment


def delete_sepa_waiting_payment(request, waiting_payment: ExpenseSepaWaitingPayment):
    """
    Delete the given waiting payment
    """
    assert not waiting_payment.payment, "Un décaissement est déjà enregistré"
    expense_sheet = waiting_payment.expense_sheet
    log_entry = request.dbsession.execute(
        select(StatusLogEntry)
        .where(
            StatusLogEntry.state_manager_key == "wait_for_payment",
            StatusLogEntry.node_id == waiting_payment.node_id,
        )
        .order_by(StatusLogEntry.id.desc())
    ).scalar()
    if log_entry is not None:
        expense_sheet.statuses.remove(log_entry)
        request.dbsession.delete(log_entry)

    expense_sheet.sepa_waiting_payments.remove(waiting_payment)
    request.dbsession.delete(waiting_payment)
    request.dbsession.flush()
    return expense_sheet


def cancel_sepa_waiting_payment(
    request, waiting_payment: ExpenseSepaWaitingPayment
) -> ExpenseSheet:
    """
    Cancel the given waiting payment (in case the bank refused the payment)
    In this situation, a payment has already been added
    """
    assert waiting_payment.paid_status == ExpenseSepaWaitingPayment.PAID_STATUS

    expense_sheet = waiting_payment.expense_sheet
    # The payment we delete
    expense_payment = waiting_payment.payment
    if expense_payment:
        delete_expense_payment(request, expense_sheet, expense_payment)
        # Pour être sûr que le paiement n'est plus associé
        # il n'est nettoyé qu'apèrs le transaction.commit()
        waiting_payment.payment = None

    waiting_payment.paid_status = waiting_payment.CANCELLED_STATUS
    request.dbsession.merge(waiting_payment)
    request.dbsession.flush()
    cancelled = strings.format_amount(
        waiting_payment.amount, precision=2, html=False, currency=True
    )
    log_entry = StatusLogEntry(
        node=expense_sheet,
        state_manager_key="wait_for_payment",
        visibility="management",
        status="valid",
        label=f"Paiement annulé : {cancelled}",
        comment="",
        user=request.identity,
    )
    request.dbsession.add(log_entry)
    request.dbsession.flush()

    return expense_sheet

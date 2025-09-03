import logging

from .document_events import StatusChangedEvent
from caerp.utils.notification.expense import notify_expense_status_changed
from caerp.events.tasks import (
    on_status_changed_alert_related_business,
)
from caerp.utils.notification.task import notify_task_status_changed
from caerp.utils.notification.supply import (
    notify_supplier_document_status_changed,
)


logger = logging.getLogger(__name__)


def notify_on_status_changed(event: StatusChangedEvent):
    """
    Dispatch the event, wrap it with a node specific wrapper and the send email
    from it
    """
    logger.info("+ StatusChangedEvent : Mail")

    if event.node_type == "expensesheet":
        notify_expense_status_changed(
            event.request, event.node, event.status, event.comment
        )

    elif event.node_type in (
        "invoice",
        "estimation",
        "internalinvoice",
        "internalestimation",
    ):
        notify_task_status_changed(
            event.request, event.node, event.status, event.comment
        )

    elif event.node_type in ("supplier_order", "supplier_invoice"):
        notify_supplier_document_status_changed(
            event.request, event.node, event.status, event.comment
        )

    else:
        logger.info(
            " - No notifications launched on {} status change".format(event.node_type)
        )
        return


def alert_related(event):
    """
    Dispatch the event to alert some related objects
    """
    logger.info("+ StatusChangedEvent : Alert")
    if event.node_type in (
        "invoice",
        "estimation",
        "internalinvoice",
        "internalestimation",
        "cancelinvoice",
    ):
        on_status_changed_alert_related_business(event)


def includeme(config):
    config.add_subscriber(notify_on_status_changed, StatusChangedEvent)
    config.add_subscriber(alert_related, StatusChangedEvent)

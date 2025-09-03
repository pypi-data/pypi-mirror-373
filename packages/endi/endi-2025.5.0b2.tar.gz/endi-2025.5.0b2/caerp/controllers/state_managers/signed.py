from typing import List

from zope.interface import implementer

from caerp.consts.permissions import PERMISSIONS
from caerp.events.document_events import StatusChangedEvent
from caerp.interfaces import ISignedStateManager
from caerp.models.action_manager import Action, ActionManager
from caerp.models.status import StatusLogEntry
from caerp.models.task import Estimation
from caerp.utils.status_rendering import SIGNED_STATUS_ICON


def _notify_status_change_event_callback(request, task, status, **kw):
    """
    Notify the change to the registry

    :param str status: The new status that was affected
    :param dict params: The submitted data transmitted with status change
    """
    request.registry.notify(StatusChangedEvent(request, task, "signed_status"))
    return task


def _record_status_change_callback(
    request, node: Estimation, status: str, **kw
) -> Estimation:
    if request.identity.id is not None:
        status_record = StatusLogEntry(
            status=status,
            node=node,
            user=request.identity,
            comment=kw.get("comment", ""),
            state_manager_key="signed_status",
        )
        request.dbsession.add(status_record)
        request.dbsession.flush()

    return node


def signed_status_callback(request, task, **kw):
    """
    Cache an acl task in the database

    :param obj request: The current pyramid request
    :param obj task: The current context
    """
    return task


def get_signed_status_actions():
    """
    Return actions available for setting the signed_status attribute on
    Estimation objects
    """
    manager = ActionManager()
    for status, label, title, css in (
        ("waiting", "En attente de réponse", "En attente de réponse du client", "btn"),
        (
            "sent",
            "A été envoyé au client",
            "A bien été envoyé au client",
            "btn",
        ),
        (
            "aborted",
            "Sans suite",
            "Marquer sans suite",
            "btn negative",
        ),
        (
            "signed",
            "Signé par le client",
            "Indiquer que le client a passé commande",
            "btn btn-primary",
        ),
    ):
        action = Action(
            status,
            permission=PERMISSIONS["context.set_signed_status_estimation"],
            status_attr="signed_status",
            icon=SIGNED_STATUS_ICON[status],
            label=label,
            title=title,
            css=css,
            callback=[signed_status_callback],
        )
        manager.add(action)
    return manager


SIGNED_ACTION_MANAGER = get_signed_status_actions()


@implementer(ISignedStateManager)
def get_default_signed_status_manager(doctype: str) -> ActionManager:
    return SIGNED_ACTION_MANAGER


def set_status(request, task: Estimation, status: str, **kw) -> Estimation:
    manager = request.find_service(ISignedStateManager, context=task)
    task = manager.process(request, task, status, **kw)
    _notify_status_change_event_callback(request, task, status, **kw)
    _record_status_change_callback(request, task, status, **kw)
    return task


def check_allowed(request, task: Estimation, status: str) -> Action:
    manager = request.find_service(ISignedStateManager, context=task)
    return manager.check_allowed(request, task, status)


def get_allowed_actions(request, task: Estimation) -> List[Action]:
    manager = request.find_service(ISignedStateManager, context=task)
    return manager.get_allowed_actions(request, task)

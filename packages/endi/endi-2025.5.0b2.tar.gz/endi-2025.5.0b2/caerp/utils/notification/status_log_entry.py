"""Notification related to mémo (StatusLogEntry)"""
import typing
from caerp.models.status import StatusLogEntry
from caerp.utils.strings import MODELS_STRINGS
from .notification import notify
from .abstract import AbstractNotification


def notify_memo_added(
    request, node, node_url, memo: StatusLogEntry, user_ids: typing.List[int]
):
    """
    Notify end users when a memo is added to a node
    Can be used to send notification to the owner of the node or to a manager
    """
    body = f"{memo.label}"
    if memo.comment:
        body = f"<strong>{body}</strong><br />{memo.comment} "
    body += f"<a href='{node_url}' title='Voir le document {node.name}'>Voir le document</a>"
    name_str = MODELS_STRINGS.get(node.__class__.__name__, {}).get("label", "")

    notify(
        request,
        AbstractNotification(
            key="node:memo:added",
            title=f"{name_str} - {memo.user.label} a ajouté un mémo",
            body=body,
        ),
        user_ids=user_ids,
    )

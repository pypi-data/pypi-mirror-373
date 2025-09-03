from typing import Optional
from sqlalchemy import func, select
from caerp.models.config import Config
from caerp.models.smtp import NodeSmtpHistory
from caerp.views.task.utils import get_task_view_type


def is_node_sent_by_email(request, task) -> bool:
    return (
        request.dbsession.execute(
            select(func.count(NodeSmtpHistory.id))
            .filter(NodeSmtpHistory.node_id == task.id)
            .filter(NodeSmtpHistory.status == NodeSmtpHistory.SUCCESS_STATUS)
        ).scalar_one()
        > 0
    )


def get_last_sent_node_smtp_history(request, task) -> Optional[NodeSmtpHistory]:
    return (
        request.dbsession.query(NodeSmtpHistory)
        .filter(NodeSmtpHistory.node_id == task.id)
        .filter(NodeSmtpHistory.status == NodeSmtpHistory.SUCCESS_STATUS)
        .order_by(NodeSmtpHistory.created_at.desc())
        .first()
    )


def get_default_task_mail_subject(request, task):
    """
    Return the default task mail subject
    """
    task_type = get_task_view_type(task)
    return Config.get_value(
        f"smtp_cae_{task_type}_subject_template", default="", type_=str
    ).format(task=task)


def get_default_task_mail_body(request, task):
    """
    Return the default task mail body
    """
    task_type = get_task_view_type(task)
    return Config.get_value(
        f"smtp_cae_{task_type}_body_template", default="", type_=str
    ).format(task=task)

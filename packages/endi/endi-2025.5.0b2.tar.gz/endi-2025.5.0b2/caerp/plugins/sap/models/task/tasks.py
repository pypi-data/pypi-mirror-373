from sqlalchemy.event import (
    listen,
    remove,
)

from caerp.models.task.task import Task
from caerp.models.listeners import SQLAListeners
from sqlalchemy.event.api import contains


def force_sap_task_fields(mapper, connection, target: Task):
    target.display_ttc = True
    target.display_units = True


def start_listening():
    listen(Task, "before_insert", force_sap_task_fields, propagate=True)
    listen(Task, "before_update", force_sap_task_fields, propagate=True)


def stop_listening():
    remove(Task, "before_insert", force_sap_task_fields)
    remove(Task, "before_update", force_sap_task_fields)


def is_listening():
    return contains(Task, "before_insert", force_sap_task_fields)


def includeme(config):
    SQLAListeners.register(start_listening, stop_listening)

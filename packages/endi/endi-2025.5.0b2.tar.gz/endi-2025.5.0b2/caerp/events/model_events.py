from sqlalchemy import event, inspect
from sqlalchemy.orm import Session

from pyramid.threadlocal import get_current_request


class BeforeModelCommit:
    """
    BeforeModelCommit event is fired in the sqlalchemy before_commit event and
    contains all model changes recorded during the current transaction

    :param obj request: The pyramid request currently running
    :param list changes: list of 2-uples (operation, model) where operation is
    one of insert/update/deleted
    """

    def __init__(self, request, changes):
        self.request = request
        self.changes = changes

    def _get_model_subset(self, operation_type):
        return [
            model for operation, model in self.changes if operation == operation_type
        ]

    def get_inserts(self):
        """
        Returns the list of models that have been inserted
        """
        return self._get_model_subset("insert")

    def get_updates(self):
        """
        Returns the list of models that have been updated
        """
        return self._get_model_subset("update")

    def get_deleted(self):
        """
        Returns the list of models that have been deleted
        """
        return self._get_model_subset("deleted")

    def get_changes_by_class(self, model_classes):
        """
        Build a dict grouping a subset of the changes containing only objects
        that are instances of one of the model_classes operation are stored by class

        >>>  models = event.get_instances_by_class([Invoice, Estimation, CancelInvoice])
        >>>  for obj in models[Invoice]:
        ...      # do your stuff

        :param list model_classes: list of model classes passed to the
        isinstance tool
        :returns: A dict in the form
        {ModelClass: [(operation, model_instance), ...], ...}
        """
        changes_subset = [
            item for item in self.changes if isinstance(item[1], model_classes)
        ]
        result = {}
        for operation, model in changes_subset:
            result.setdefault(model.__class__, []).append((operation, model))
        return result


class ModelChangeEventManager:
    @classmethod
    def register(cls, session):
        if not hasattr(session, "_model_changes"):
            session._model_changes = {}

        event.listen(session, "before_flush", cls.record_ops)
        event.listen(session, "before_commit", cls.record_ops)
        event.listen(session, "before_commit", cls.before_commit)
        event.listen(session, "after_commit", cls.after_commit)
        event.listen(session, "after_rollback", cls.after_rollback)

    @classmethod
    def unregister(cls, session):
        if hasattr(session, "_model_changes"):
            del session._model_changes

        event.remove(session, "before_flush", cls.record_ops)
        event.remove(session, "before_commit", cls.record_ops)
        event.remove(session, "before_commit", cls.before_commit)
        event.remove(session, "after_commit", cls.after_commit)
        event.remove(session, "after_rollback", cls.after_rollback)

    @staticmethod
    def record_ops(session, flush_context=None, instances=None):
        try:
            model_changes = session._model_changes
        except AttributeError:
            return

        for operation, targets in (
            ("insert", session.new),
            ("update", session.dirty),
            ("delete", session.deleted),
        ):
            for target in targets:
                state = inspect(target)
                key = state.identity_key if state.has_identity else id(target)
                if key not in model_changes:
                    model_changes[key] = (operation, target)

    @staticmethod
    def before_commit(session):
        try:
            model_changes = session._model_changes
        except AttributeError:
            return

        if model_changes:
            request = get_current_request()
            if hasattr(request, "registry"):
                request.registry.notify(
                    BeforeModelCommit(request, changes=list(model_changes.values()))
                )

    @staticmethod
    def after_commit(session):
        model_changes = getattr(session, "_model_changes", None)
        if model_changes:
            model_changes.clear()

    @staticmethod
    def after_rollback(session):
        model_changes = getattr(session, "_model_changes", None)
        if model_changes:
            model_changes.clear()


def includeme(config):
    ModelChangeEventManager.register(Session)

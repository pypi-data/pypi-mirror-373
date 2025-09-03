import logging


logger = logging.getLogger(__name__)


class FileAdded:
    """
    Event to be fired on new file download

    >>> request.registry.notify(
    ...     FileAdded(request, file_object, current_form_data)
    ... )
    """

    action = "add"

    def __init__(self, request, file_object, current_form_data=None):
        self.request = request
        self.file_object = file_object
        self.parent = self.file_object.parent
        if current_form_data is not None:
            self.form_data = current_form_data
        else:
            self.form_data = {}


class FileUpdated(FileAdded):
    """
    Event to be fired on file update

    >>> request.registry.notify(FileUpdated(request, file_object))
    """

    action = "update"


class FileDeleted(FileAdded):
    """
    Event fired when a file was deleted
    >>> request.registry.notify(FileDeleted(request, file_object))
    """

    action = "delete"


def on_file_change(event):
    if hasattr(event.parent, "file_requirement_service"):
        logger.info(
            f"+ Calling the parent's file requirement service {event.file_object.parent_id}"
            f" {event.action}"
        )
        event.parent.file_requirement_service.register(
            event.parent, event.file_object, action=event.action
        )
        if hasattr(event.parent, "status_service"):
            event.parent.status_service.update_status(
                event.parent,
            )

    from caerp.models.user.userdatas import UserDatas

    if isinstance(event.parent, UserDatas):
        from caerp.models.career_path import save_file_careerpath_relationship

        save_file_careerpath_relationship(
            event.request, event.form_data, event.file_object
        )


def includeme(config):
    config.add_subscriber(on_file_change, FileAdded)

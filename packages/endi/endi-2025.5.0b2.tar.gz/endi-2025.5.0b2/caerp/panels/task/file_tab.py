from caerp.views.task.utils import get_task_url
from caerp.panels.files import stream_actions


def task_file_tab_panel(context, request, title, add_url=None):
    """
    Collect data used to render the file tab panel

    :param obj context: The context for which we display the files
    :param str title: The title to give to this tab
    :param str add_url: The url for adding elements
    :returns: dict
    """
    if add_url is None:
        add_url = get_task_url(request, context, suffix="/addfile")

    return dict(
        title=title,
        add_url=add_url,
        files=context.files,
        stream_actions=stream_actions,
    )


def includeme(config):
    config.add_panel(
        task_file_tab_panel,
        "task_file_tab",
        renderer="panels/task/file_tab.mako",
    )

from caerp.consts.permissions import PERMISSIONS
from caerp.utils.widgets import (
    Link,
    POSTButton,
)
from caerp.models.project import Project

from caerp.views.company.routes import (
    COMPANY_ESTIMATION_ADD_ROUTE,
    COMPANY_INVOICE_ADD_ROUTE,
)
from caerp.views.task.utils import (
    get_task_url,
    get_task_view_type,
)


def _stream_actions(request, item):
    """
    Return actions that will be rendered in a dropdown
    """
    task_type = get_task_view_type(item)
    yield Link(get_task_url(request, item), "Voir / Modifier", icon="pen", css="icon")
    yield Link(
        get_task_url(request, item, suffix=".pdf"),
        "PDF",
        title="Enregistrer le PDF",
        icon="file-pdf",
        css="icon",
    )
    if request.has_permission(PERMISSIONS[f"context.duplicate_{task_type}"], item):
        yield Link(
            get_task_url(request, item, suffix="/duplicate"),
            "Dupliquer",
            icon="copy",
            css="icon",
        )

    if request.has_permission(PERMISSIONS[f"context.delete_{task_type}"], item):
        yield POSTButton(
            get_task_url(request, item, suffix="/delete"),
            "Supprimer",
            confirm="Êtes-vous sûr de vouloir supprimer ce document ?",
            icon="trash-alt",
            css="icon negative",
        )

    for phase in request.context.phases:
        if phase.id != item.phase_id:
            yield POSTButton(
                get_task_url(request, item, suffix="/move", _query={"phase": phase.id}),
                "Déplacer vers le sous-dossier %s" % phase.name,
                icon="arrows-alt-v",
                css="icon",
            )


def phase_estimations_panel(context: Project, request, phase, estimations):
    """
    Phase estimation list panel
    """
    _query = {"project_id": context.id}
    if phase is not None:
        _query["phase_id"] = phase.id

    add_url = request.route_path(
        COMPANY_ESTIMATION_ADD_ROUTE, id=context.company_id, _query=_query
    )

    return dict(
        add_url=add_url,
        estimations=estimations,
        stream_actions=_stream_actions,
    )


def phase_invoices_panel(context: Project, request, phase, invoices):
    """
    Phase invoice list panel
    """
    _query = {"project_id": context.id}
    if phase is not None:
        _query["phase_id"] = phase.id

    add_url = request.route_path(
        COMPANY_INVOICE_ADD_ROUTE, id=context.company_id, _query=_query
    )

    return dict(
        add_url=add_url,
        invoices=invoices,
        stream_actions=_stream_actions,
    )


def includeme(config):
    config.add_panel(
        phase_estimations_panel,
        "phase_estimations",
        renderer="caerp:templates/panels/project/phase_estimations.mako",
    )
    config.add_panel(
        phase_invoices_panel,
        "phase_invoices",
        renderer="caerp:templates/panels/project/phase_invoices.mako",
    )

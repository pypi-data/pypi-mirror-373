"""
Panel pour le dashboard admin
"""
from caerp.models.task import Task
from caerp.views.task.utils import get_task_url


def manage_dashboard_estimations_panel(context, request):
    """
    Panel displaying waiting estimations to the end user
    """
    # DEVIS
    estimations = Task.get_waiting_estimations().all()
    for item in estimations:
        item.url = get_task_url(request, item)
    return {
        "dataset": estimations,
        "title": "Devis en attente de validation",
        "icon": "file-list",
        "file_hint": "Voir le devis",
    }


def manage_dashboard_invoices_panel(context, request):
    """
    Panel displaying waiting invoices to the end user
    """
    # FACTURES
    invoices = Task.get_waiting_invoices().all()
    for item in invoices:
        item.url = get_task_url(request, item)

    return {
        "dataset": invoices,
        "title": "Factures et Avoirs en attente de validation",
        "icon": "file-invoice-euro",
        "file_hint": "Voir la facture",
    }


def includeme(config):
    config.add_panel(
        manage_dashboard_estimations_panel,
        "manage_dashboard_estimations",
        renderer="caerp:templates/panels/manage/" "manage_dashboard_waiting_docs.mako",
    )
    config.add_panel(
        manage_dashboard_invoices_panel,
        "manage_dashboard_invoices",
        renderer="caerp:templates/panels/manage/" "manage_dashboard_waiting_docs.mako",
    )

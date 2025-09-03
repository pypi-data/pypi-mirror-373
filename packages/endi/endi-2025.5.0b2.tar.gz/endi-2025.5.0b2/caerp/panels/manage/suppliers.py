"""
Panel listant les commandes / factures fournisseurs en attente
"""
from caerp.interfaces import IValidationStatusHolderService
from caerp.models.supply import (
    SupplierInvoice,
    SupplierOrder,
)


def manage_dashboard_supply_panel(context, request):
    # COMMANDES/FACTURES FORUNISSEURS
    status_docs_service = request.find_service(IValidationStatusHolderService)
    supply_docs = list(status_docs_service.waiting(SupplierOrder, SupplierInvoice))
    for doc in supply_docs:
        if isinstance(doc, SupplierOrder):
            doc.url = request.route_path("/supplier_orders/{id}", id=doc.id)
        elif isinstance(doc, SupplierInvoice):
            doc.url = request.route_path("/supplier_invoices/{id}", id=doc.id)
        else:
            raise ValueError()
    return {
        "title": "Commandes et factures fournisseur",
        "dataset": supply_docs,
        "icon": "box",
        "file_hint": "Voir le document",
    }


def includeme(config):
    config.add_panel(
        manage_dashboard_supply_panel,
        "manage_dashboard_supply",
        renderer="caerp:templates/panels/manage/" "manage_dashboard_waiting_docs.mako",
    )

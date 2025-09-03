import os

from caerp.views import caerp_add_route

COLLECTION_ROUTE = "/supplier_invoices"
COLLECTION_EXPORT_ROUTE = "/supplier_invoices.{extension}"
ITEM_ROUTE = os.path.join(COLLECTION_ROUTE, "{id}")
ADD_TO_SEPA_URL = os.path.join(ITEM_ROUTE, "add_to_sepa", "{type}")
COMPANY_COLLECTION_ROUTE = "/companies/{id}/supplier_invoices"
COMPANY_COLLECTION_EXPORT_ROUTE = "/companies/{id}/supplier_invoices.{extension}"
DISPATCH_ROUTE = "/dispatch_supplier_invoice"
FILE_EXPORT_ROUTE = "/supplier_invoices/export/files"

API_COLLECTION_ROUTE = "/api/v1/supplier_invoices"
API_ITEM_ROUTE = os.path.join(API_COLLECTION_ROUTE, "{id}")
API_LINE_COLLECTION_ROUTE = os.path.join(API_ITEM_ROUTE, "lines")
API_LINE_ITEM_ROUTE = os.path.join(API_LINE_COLLECTION_ROUTE, "{line_id}")
API_STATUS_LOG_ENTRIES_ROUTE = os.path.join(API_ITEM_ROUTE, "statuslogentries")
API_STATUS_LOG_ENTRY_ITEM_ROUTE = os.path.join(
    API_STATUS_LOG_ENTRIES_ROUTE, "{status_id}"
)


def includeme(config):
    for route in (COLLECTION_ROUTE, COLLECTION_EXPORT_ROUTE):
        config.add_route(route, route)

    for route in (COMPANY_COLLECTION_ROUTE, COMPANY_COLLECTION_EXPORT_ROUTE):
        caerp_add_route(
            config,
            route,
            traverse="/companies/{id}",
        )

    caerp_add_route(
        config,
        ITEM_ROUTE,
        traverse="/supplier_invoices/{id}",
    )
    caerp_add_route(config, ADD_TO_SEPA_URL, traverse="/supplier_invoices/{id}")
    for action in (
        "delete",
        "duplicate",
        "addfile",
        "set_types",
    ):
        route = os.path.join(ITEM_ROUTE, action)
        caerp_add_route(
            config,
            route,
            traverse="/supplier_invoices/{id}",
        )
    config.add_route(DISPATCH_ROUTE, DISPATCH_ROUTE)
    config.add_route(FILE_EXPORT_ROUTE, FILE_EXPORT_ROUTE)

    config.add_route(API_COLLECTION_ROUTE, API_COLLECTION_ROUTE)

    for route in [
        API_ITEM_ROUTE,
        API_LINE_COLLECTION_ROUTE,
        API_STATUS_LOG_ENTRIES_ROUTE,
    ]:
        config.add_route(
            route,
            route,
            traverse="/supplier_invoices/{id}",
        )

    config.add_route(
        API_LINE_ITEM_ROUTE,
        API_LINE_ITEM_ROUTE,
        traverse="/supplier_invoicelines/{line_id}",
    )

    config.add_route(
        API_STATUS_LOG_ENTRY_ITEM_ROUTE,
        API_STATUS_LOG_ENTRY_ITEM_ROUTE,
        traverse="/statuslogentries/{status_id}",
    )

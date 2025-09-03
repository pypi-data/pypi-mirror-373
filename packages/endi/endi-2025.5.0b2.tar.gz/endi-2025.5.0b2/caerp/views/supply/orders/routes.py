import os

COLLECTION_ROUTE = "/supplier_orders"
ITEM_ROUTE = os.path.join(COLLECTION_ROUTE, "{id}")
COMPANY_COLLECTION_ROUTE = "/companies/{id}/supplier_orders"
API_COLLECTION_ROUTE = "/api/v1/supplier_orders"
API_ITEM_ROUTE = os.path.join(API_COLLECTION_ROUTE, "{id}")
API_LINE_COLLECTION_ROUTE = os.path.join(API_ITEM_ROUTE, "lines")
API_LINE_ITEM_ROUTE = os.path.join(API_LINE_COLLECTION_ROUTE, "{line_id}")
API_STATUS_LOG_ENTRIES_ROUTE = os.path.join(API_ITEM_ROUTE, "statuslogentries")
API_STATUS_LOG_ENTRY_ITEM_ROUTE = os.path.join(
    API_STATUS_LOG_ENTRIES_ROUTE, "{status_id}"
)


def includeme(config):
    config.add_route(COLLECTION_ROUTE, COLLECTION_ROUTE)

    config.add_route(
        COMPANY_COLLECTION_ROUTE,
        COMPANY_COLLECTION_ROUTE,
        traverse="/companies/{id}",
    )

    config.add_route(
        ITEM_ROUTE,
        ITEM_ROUTE,
        traverse="/supplier_orders/{id}",
    )
    for action in (
        "delete",
        "duplicate",
        "addfile",
    ):
        route = f"{ITEM_ROUTE}/{action}"
        config.add_route(
            route,
            route,
            traverse="/supplier_orders/{id}",
        )

    config.add_route(API_COLLECTION_ROUTE, API_COLLECTION_ROUTE)
    for route in [
        API_ITEM_ROUTE,
        API_LINE_COLLECTION_ROUTE,
        API_STATUS_LOG_ENTRIES_ROUTE,
    ]:
        config.add_route(
            route,
            route,
            traverse="/supplier_orders/{id}",
        )

    config.add_route(
        API_LINE_ITEM_ROUTE,
        API_LINE_ITEM_ROUTE,
        traverse="/supplier_orderlines/{line_id}",
    )

    config.add_route(
        API_STATUS_LOG_ENTRY_ITEM_ROUTE,
        API_STATUS_LOG_ENTRY_ITEM_ROUTE,
        traverse="/statuslogentries/{status_id}",
    )

from caerp.views import caerp_add_route, redirect_to_index_view

COLLECTION_ROUTE = "/companies"
COLLECTION_ROUTE_v2 = "/companies_v2"
COLLECTION_MAP_ROUTE = "/companies_map"

ITEM_ROUTE = "/companies/{id}"
DASHBOARD_ROUTE = "/companies/{id}/dashboard"
OLD_DASHBOARD_ROUTE = "/company/{id}/dashboard"
API_ROUTE = "/api/v1/companies"
API_ROUTE_GEOJSON = "/api/v1/companies.geojson"
API_ITEM_ROUTE = "/api/v1/companies/{id}"

API_LOGO_ROUTE = "/api/v1/companies/logo"
API_LOGO_ITEM_ROUTE = API_LOGO_ROUTE + "/{id}"
API_HEADER_ROUTE = "/api/v1/companies/header"
API_HEADER_ITEM_ROUTE = API_HEADER_ROUTE + "/{id}"
API_STATUS_LOG_ENTRIES_ROUTE = "/api/v1/companies/{id}/statuslogentries"

COMPANY_ESTIMATIONS_ROUTE = "/companies/{id}/estimations"
COMPANY_ESTIMATION_ADD_ROUTE = "/companies/{id}/estimations/add"
COMPANY_INVOICES_ROUTE = "/companies/{id}/invoices"
COMPANY_INVOICE_ADD_ROUTE = "/companies/{id}/invoices/add"


def includeme(config):
    """
    Configure routes for this module
    """
    caerp_add_route(config, COLLECTION_ROUTE)
    caerp_add_route(config, COLLECTION_ROUTE_v2)
    caerp_add_route(config, COLLECTION_MAP_ROUTE)
    config.add_view(redirect_to_index_view, route_name=OLD_DASHBOARD_ROUTE)
    caerp_add_route(config, API_ROUTE)
    caerp_add_route(config, API_ROUTE_GEOJSON)

    traverse = "/companies/{id}"
    for route in (
        ITEM_ROUTE,
        DASHBOARD_ROUTE,
        OLD_DASHBOARD_ROUTE,
        COMPANY_ESTIMATIONS_ROUTE,
        COMPANY_ESTIMATION_ADD_ROUTE,
        COMPANY_INVOICES_ROUTE,
        COMPANY_INVOICE_ADD_ROUTE,
        API_ITEM_ROUTE,
        API_STATUS_LOG_ENTRIES_ROUTE,
    ):
        caerp_add_route(config, route, traverse=traverse)

    caerp_add_route(
        config,
        "/api/v1/companies/{eid}/statuslogentries/{id}",
        traverse="/statuslogentries/{id}",
    )

    # routes for logo handling
    caerp_add_route(config, API_LOGO_ROUTE)
    caerp_add_route(
        config,
        API_LOGO_ITEM_ROUTE,
        traverse="/files/{id}",
    )

    # routes for header handling
    caerp_add_route(config, API_HEADER_ROUTE)
    caerp_add_route(
        config,
        API_HEADER_ITEM_ROUTE,
        traverse="/files/{id}",
    )

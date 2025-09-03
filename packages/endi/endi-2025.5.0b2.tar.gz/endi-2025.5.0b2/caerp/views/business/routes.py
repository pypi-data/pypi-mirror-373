import os
from caerp.views import caerp_add_route

COMPANY_BUSINESSES_ROUTE = "/companies/{id}/businesses"
BUSINESSES_ROUTE = "/businesses"
BUSINESS_ITEM_ROUTE = os.path.join(BUSINESSES_ROUTE, "{id}")
BUSINESS_ITEM_OVERVIEW_ROUTE = os.path.join(BUSINESS_ITEM_ROUTE, "overview")
BUSINESS_ITEM_ESTIMATION_ROUTE = os.path.join(BUSINESS_ITEM_ROUTE, "estimations")
BUSINESS_ITEM_EXPENSES_ROUTE = os.path.join(BUSINESS_ITEM_ROUTE, "expenses")
BUSINESS_ITEM_EXPENSES_UNLINK_ROUTE = os.path.join(
    BUSINESS_ITEM_EXPENSES_ROUTE, "unlink/{type}/{line_id}"
)
BUSINESS_ITEM_INVOICE_ROUTE = os.path.join(BUSINESS_ITEM_ROUTE, "invoices")
BUSINESS_ITEM_INVOICE_EXPORT_ROUTE = BUSINESS_ITEM_INVOICE_ROUTE + ".{extension}"
BUSINESS_ITEM_FILE_ROUTE = os.path.join(BUSINESS_ITEM_ROUTE, "files")
BUSINESS_ITEM_FILE_ZIP_ROUTE = os.path.join(BUSINESS_ITEM_ROUTE, "files.zip")
BUSINESS_ITEM_ADD_FILE_ROUTE = os.path.join(BUSINESS_ITEM_ROUTE, "addfile")
BUSINESS_ITEM_PY3O_ROUTE = os.path.join(BUSINESS_ITEM_ROUTE, "py3o")
BUSINESS_ITEM_INVOICING_ALL_ROUTE = os.path.join(BUSINESS_ITEM_ROUTE, "invoicing")
BUSINESS_ITEM_INVOICING_ROUTE = os.path.join(
    BUSINESS_ITEM_INVOICING_ALL_ROUTE,
    "{deadline_id}",
)
BUSINESS_ITEM_PROGRESS_INVOICING_ROUTE = os.path.join(
    BUSINESS_ITEM_ROUTE, "add_progress_invoicing_invoice"
)
BUSINESS_PAYMENT_DEADLINE_ITEM_ROUTE = "/business_payment_deadlines/{id}"

BUSINESS_ITEM_API = "/api/v1/businesses/{id}"
BUSINESS_TREE_API = "/api/v1/businesses/{id}/tree"
COMPANY_ITEM_BUSINESSES_API = "/api/v1/companies/{id}/businesses"
BUSINESS_TEMPLATE_COLLECTION_API = "/api/v1/businesses/{id}/templates"
BUSINESS_LIST_URL = "/businesses_lists"


def includeme(config):
    caerp_add_route(
        config,
        COMPANY_BUSINESSES_ROUTE,
        traverse="/companies/{id}",
    )
    for route in (
        BUSINESS_ITEM_ROUTE,
        BUSINESS_ITEM_OVERVIEW_ROUTE,
        BUSINESS_ITEM_ESTIMATION_ROUTE,
        BUSINESS_ITEM_EXPENSES_ROUTE,
        BUSINESS_ITEM_EXPENSES_UNLINK_ROUTE,
        BUSINESS_ITEM_INVOICE_ROUTE,
        BUSINESS_ITEM_INVOICE_EXPORT_ROUTE,
        BUSINESS_ITEM_FILE_ROUTE,
        BUSINESS_ITEM_FILE_ZIP_ROUTE,
        BUSINESS_ITEM_ADD_FILE_ROUTE,
        BUSINESS_ITEM_PY3O_ROUTE,
        BUSINESS_ITEM_INVOICING_ROUTE,
        BUSINESS_ITEM_INVOICING_ALL_ROUTE,
        BUSINESS_ITEM_PROGRESS_INVOICING_ROUTE,
        BUSINESS_ITEM_API,
        BUSINESS_TREE_API,
        BUSINESS_TEMPLATE_COLLECTION_API,
    ):
        caerp_add_route(config, route, traverse="/businesses/{id}")

    for route in (BUSINESS_PAYMENT_DEADLINE_ITEM_ROUTE,):
        caerp_add_route(config, route, traverse="/business_payment_deadlines/{id}")

    caerp_add_route(
        config,
        COMPANY_ITEM_BUSINESSES_API,
        traverse="/companies/{id}",
    )
    caerp_add_route(config, BUSINESSES_ROUTE)

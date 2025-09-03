import os

UPLOAD_ROUTE = "/accounting/operation_uploads"
UPLOAD_ITEM_ROUTE = os.path.join(UPLOAD_ROUTE, "{id}")
UPLOAD_ITEM_ROUTE_EXPORT = os.path.join(UPLOAD_ITEM_ROUTE, "operations.{extension}")
UPLOAD_ITEM_TREASURY_ROUTE = os.path.join(UPLOAD_ITEM_ROUTE, "treasury_measure_grids")
UPLOAD_ITEM_INCOME_STATEMENT_ROUTE = os.path.join(
    UPLOAD_ITEM_ROUTE, "income_statement_measure_grids"
)

COMPANY_TREASURY_ROUTE = "/companies/{id}/accounting/treasury_measure_grids"
TREASURY_ITEM_ROUTE = "/treasury_measure_grids/{id}"

COMPANY_BALANCE_SHEET_ROUTE = "/companies/{id}/accounting/balance_sheet_measure_grids"

INCOME_STATEMENT_GRIDS_ROUTE = (
    "/companies/{id}/accounting/income_statement_measure_grids"
)
INCOME_STATEMENT_GRIDS_ROUTE_EXPORT = (
    "/companies/{id}/accounting/income_statement_measure_grids.{extension}"
)

BANK_REMITTANCE_ROUTE = "/accounting/bank_remittances"
BANK_REMITTANCE_ITEM_ROUTE = os.path.join(BANK_REMITTANCE_ROUTE, "{id}")

COMPANY_GENERAL_LEDGER_OPERATION = (
    "/companies/{id}/accounting/general_ledger_operation_list"
)

COMPANY_GENERAL_LEDGER_OPERATION_EXPORT = (
    "/companies/{id}/accounting/grand_livre.{extension}"
)


def includeme(config):
    config.add_route(UPLOAD_ROUTE, UPLOAD_ROUTE)
    for route in (
        UPLOAD_ITEM_ROUTE,
        UPLOAD_ITEM_TREASURY_ROUTE,
        UPLOAD_ITEM_INCOME_STATEMENT_ROUTE,
    ):
        config.add_route(route, route, traverse="/accounting_operation_uploads/{id}")

    for i in (
        COMPANY_BALANCE_SHEET_ROUTE,
        COMPANY_TREASURY_ROUTE,
        INCOME_STATEMENT_GRIDS_ROUTE,
        INCOME_STATEMENT_GRIDS_ROUTE_EXPORT,
        COMPANY_GENERAL_LEDGER_OPERATION,
    ):
        config.add_route(i, i, traverse="/companies/{id}")

    config.add_route(
        TREASURY_ITEM_ROUTE,
        TREASURY_ITEM_ROUTE,
        traverse="/treasury_measure_grids/{id}",
    )
    config.add_route(BANK_REMITTANCE_ROUTE, BANK_REMITTANCE_ROUTE)
    config.add_route(
        BANK_REMITTANCE_ITEM_ROUTE,
        BANK_REMITTANCE_ITEM_ROUTE,
        traverse="/bank_remittances/{id}",
    )
    config.add_route(
        "bank_remittance.pdf",
        "/bank_remittances/{id}.pdf",
        traverse="/bank_remittances/{id}",
    )
    config.add_route(
        "bank_remittance.csv",
        "/bank_remittances/{id}.csv",
        traverse="/bank_remittances/{id}",
    )
    config.add_route(
        "grand_livre.{extension}",
        COMPANY_GENERAL_LEDGER_OPERATION_EXPORT,
        traverse="/companies/{id}",
    )
    config.add_route(
        "operations.{extension}",
        UPLOAD_ITEM_ROUTE_EXPORT,
        traverse="/accounting_operation_uploads/{id}",
    )

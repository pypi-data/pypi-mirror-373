"""
Document statuses presentation

Centralize in a place (here) css classes (which handle colors) and icons to use
for document statuses.
"""

# Devis
SIGNED_STATUS_ICON = dict(
    (
        ("waiting", "clock"),
        ("sent", "envelope"),
        ("aborted", "times"),
        ("signed", "signature"),
    )
)

# ExpenseSheet / SupplierInvoice
JUSTIFIED_STATUS_ICON = dict(
    (
        ("waiting", "clock"),
        ("justified", "check"),
    )
)


# Catch-all : couvre autant de cas que possible
STATUS_ICON = dict(
    (
        ("draft", "pen"),
        ("wait", "clock"),
        ("valid", "check-circle"),
        ("invalid", "times-circle"),
        ("aborted", "times"),
        ("geninv", "euro-sign"),
        ("invoiced", "euro-sign"),
        ("justified", "file-check"),
        ("paid", "euro-sign"),
        ("resulted", "euro-sign"),
        ("sent", "envelope"),
        ("signed", "signature"),
        ("waiting", "euro-slash"),
        # urssaf3p_registration_status
        ("disabled", "times-circle"),
    )
)
SUPPLIER_ORDER_STATUS_ICON = STATUS_ICON
ESTIMATION_STATUS_ICON = STATUS_ICON
INVOICE_STATUS_ICON = STATUS_ICON
EXPENSE_STATUS_ICON = STATUS_ICON

# Catch-all : couvre autant de cas que possible
STATUS_CSS_CLASS = dict(
    (
        ("draft", "draft"),
        ("wait", "caution"),
        ("valid", "valid"),
        ("invalid", "invalid"),
        ("geninv", "completed"),
        ("waiting", "neutral"),
        ("sent", "neutral"),
        ("signed", "neutral"),
        ("aborted", "closed"),
        # paid_status
        ("resulted", "valid"),
        ("paid", "partial_invalid"),
        # urssaf3p_registration_status
        ("disabled", "invalid"),
    )
)

JUSTIFIED_STATUS_CSS_CLASS = dict(
    (
        ("justified", "valid"),
        ("waiting", "caution"),
    )
)

EXPENSE_STATUS_CSS_CLASS = dict(
    (
        ("resulted", "valid"),
        ("paid", "partial_caution"),
    )
)
SALE_DOCTYPE_ICON = {
    "estimation": "file-list",
    "invoice": "file-invoice-euro",
    "internalestimation": "file-list",
    "internalinvoice": "file-invoice-euro",
    "cancelinvoice": "file-invoice-euro",
    "internalcancelinvoice": "file-invoice-euro",
    "business": "list-alt",
    "project": "folder",
}
INDICATOR_MAIN_STATUS_ICON = {
    "wait": "clock-circle",
    "valid": "check-circle",
    "invalid": "times",
    "success": "check-circle",
    "danger": "danger",
    "warning": "warning",
}

INDICATOR_MAIN_STATUS_CSS = {
    "wait": "caution",
    "valid": "success",
    "invalid": "invalid",
    "success": "success",
    "danger": "invalid",
    "warning": "caution",
}

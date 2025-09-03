import deform
from sqlalchemy import or_
import typing
from caerp.models.task import Task, Invoice, CancelInvoice
from caerp.forms.export import (
    PeriodSchema,
    AllSchema,
    BPFYearSchema,
    InvoiceNumberSchema,
    InvoicePeriodSchema,
    InvoiceAllSchema,
    PaymentAllSchema,
    PaymentPeriodSchema,
    ExpensePaymentPeriodSchema,
    ExpensePaymentAllSchema,
    ExpenseSchema,
    ExpenseNumberSchema,
    ExpenseAllSchema,
    SupplierInvoiceNumberSchema,
    SupplierInvoiceSchema,
    SupplierInvoiceAllSchema,
    SupplierInvoicePeriodSchema,
    SupplierPaymentAllSchema,
    SupplierPaymentPeriodSchema,
    SupplierPaymentNumberSchema,
)


EXPORT_BTN = deform.Button(name="submit", type="submit", title="Exporter")
EXPORT_PREVIEW_BTN = deform.Button(
    name="preview", type="submit", title="Prévisualiser les écritures à exporter"
)

ACCOUNTING_EXPORT_TYPE_INVOICES = "invoices"
ACCOUNTING_EXPORT_TYPE_PAYMENTS = "payments"
ACCOUNTING_EXPORT_TYPE_EXPENSES = "expenses"
ACCOUNTING_EXPORT_TYPE_EXPENSE_PAYMENTS = "expense_payments"
ACCOUNTING_EXPORT_TYPE_SUPPLIER_INVOICES = "supplier_invoices"
ACCOUNTING_EXPORT_TYPE_SUPPLIER_PAYMENTS = "supplier_payments"

ACCOUNTING_EXPORT_TYPE_OPTIONS = (
    ACCOUNTING_EXPORT_TYPE_INVOICES,
    ACCOUNTING_EXPORT_TYPE_PAYMENTS,
    ACCOUNTING_EXPORT_TYPE_EXPENSES,
    ACCOUNTING_EXPORT_TYPE_EXPENSE_PAYMENTS,
    ACCOUNTING_EXPORT_TYPE_SUPPLIER_INVOICES,
    ACCOUNTING_EXPORT_TYPE_SUPPLIER_PAYMENTS,
)

HELPMSG_CONFIG = """Des éléments de configuration sont manquants ou invalides, veuillez
<a href='{0}' target='_blank' title='La configuration s’ouvrira dans une nouvelle 
fenêtre' aria-label='La configuration s’ouvrira dans une nouvelle fenêtre'>configurer 
les informations comptables nécessaires à l'export des documents</a>"""


def find_task_status_date(official_number: str, year: typing.Optional[int] = None):
    """
    Query the database to retrieve a task with the given number and year and
    returns its status_date

    :param str official_number: The official number
    :param int year: The financial year associated to the invoice
    :returns: The document's status_date
    :rtype: datetime.dateime
    """
    return Task.find_task_status_date(official_number, year)


def query_invoices_for_export(
    start_number=None,
    end_number=None,
    year=None,
    start_date=None,
    end_date=None,
    **kwargs,
):
    """
    Build a query to get a range of tasks between two dates

    start_number/end_number are converted to the associated task date

    :param str start_number: First invoice we want to export
    :param str end_number: Last invoice we want to export
    :param int year: The financial_year (for number export)
    :param date start_date: The start_date for the export
    :param date end_date: The end date for the export
    :param dict kwargs: Dict of options passed to the Task.get_valid_invoices
    query
    """
    query = Task.get_valid_invoices(**kwargs)
    if start_number:
        start_status_date = find_task_status_date(start_number, year)
        query = query.filter(Task.status_date >= start_status_date)

    if end_number:
        end_status_date = find_task_status_date(end_number, year)
        query = query.filter(Task.status_date <= end_status_date)

    if year:
        query = query.filter(
            or_(Invoice.financial_year == year, CancelInvoice.financial_year == year)
        )

    if start_date:
        query = query.filter(Task.date >= start_date)

    if end_date:
        query = query.filter(Task.date <= end_date)

    return query.order_by(Task.status_date)


def get_expense_all_form(
    request,
    counter,
    title="Exporter les dépenses non exportées",
    prefix="",
):
    """
    Return a void form used to export all non-exported documents

    :param obj counter: An iterator used for form id generation
    """
    schema = ExpenseAllSchema(title=title)
    schema = schema.bind(request=request, prefix=prefix)
    formid = "%s_all_form" % prefix
    return deform.Form(
        schema=schema,
        buttons=(
            EXPORT_BTN,
            EXPORT_PREVIEW_BTN,
        ),
        formid=formid,
        counter=counter,
        with_loader=False,
    )


def get_invoice_all_form(request):
    """
    Return a void form used to export all non-exported documents
    """
    schema = InvoiceAllSchema()
    schema = schema.bind(request=request)
    formid = "all_form"
    return deform.Form(
        schema=schema,
        buttons=(
            EXPORT_BTN,
            EXPORT_PREVIEW_BTN,
        ),
        formid=formid,
        with_loader=False,
    )


def get_invoice_number_form(
    request, counter, title="Exporter les factures à partir d'un numéro"
):
    """
    Return the search form used to search invoices by number+year
    """
    schema = InvoiceNumberSchema(title=title)
    schema = schema.bind(request=request)
    return deform.Form(
        schema=schema,
        buttons=(
            EXPORT_BTN,
            EXPORT_PREVIEW_BTN,
        ),
        formid="invoice_number_form",
        counter=counter,
        with_loader=False,
    )


def get_invoice_period_form(
    request, counter, title="Exporter les factures sur une période donnée"
):
    """
    Return the period search form

    :param obj counter: An iterator used for form id generation
    """
    schema = InvoicePeriodSchema(title=title)
    schema = schema.bind(request=request)
    return deform.Form(
        schema=schema,
        buttons=(
            EXPORT_BTN,
            EXPORT_PREVIEW_BTN,
        ),
        formid="period_form",
        counter=counter,
        with_loader=False,
    )


def get_payment_all_form(request):
    """
    Return a void form used to export all non-exported documents
    """
    schema = PaymentAllSchema()
    schema = schema.bind(request=request)
    formid = "all_form"
    return deform.Form(
        schema=schema,
        buttons=(
            EXPORT_BTN,
            EXPORT_PREVIEW_BTN,
        ),
        formid=formid,
        with_loader=False,
    )


def get_payment_period_form(request, counter):
    """
    Return the period search form

    :param obj counter: An iterator used for form id generation
    """
    schema = PaymentPeriodSchema()
    schema = schema.bind(request=request)
    return deform.Form(
        schema=schema,
        buttons=(
            EXPORT_BTN,
            EXPORT_PREVIEW_BTN,
        ),
        formid="period_form",
        counter=counter,
        with_loader=False,
    )


def get_expense_payment_period_form(request):
    """
    Return the period search form
    """
    schema = ExpensePaymentPeriodSchema()
    schema = schema.bind(request=request)
    return deform.Form(
        schema=schema,
        buttons=(
            EXPORT_BTN,
            EXPORT_PREVIEW_BTN,
        ),
        formid="period_form",
        with_loader=False,
    )


def get_expense_payment_all_form(request, counter):
    """
    Return a void form used to export all non-exported documents

    :param obj counter: An iterator used for form id generation
    """
    schema = ExpensePaymentAllSchema()
    schema = schema.bind(request=request)
    formid = "all_form"
    return deform.Form(
        schema=schema,
        buttons=(
            EXPORT_BTN,
            EXPORT_PREVIEW_BTN,
        ),
        formid=formid,
        counter=counter,
        with_loader=False,
    )


def get_expense_number_form(request, counter, title, prefix="expense"):
    """
    Return a form for expense export by official number
    :param counter: the iterator used to insert various forms in the same page
    """
    schema = ExpenseNumberSchema(title=title)
    schema = schema.bind(request=request, prefix=prefix)
    return deform.Form(
        schema=schema,
        buttons=(
            EXPORT_BTN,
            EXPORT_PREVIEW_BTN,
        ),
        formid="%s_number_form" % prefix,
        counter=counter,
        with_loader=False,
    )


def get_expense_form(request, counter, title, prefix="expense"):
    """
    Return a form for expense export
    :param obj request: Pyramid request object
    :returns: class:`deform.Form`

    """
    schema = ExpenseSchema(title=title)
    schema = schema.bind(request=request, prefix=prefix)
    return deform.Form(
        schema=schema,
        buttons=(
            EXPORT_BTN,
            EXPORT_PREVIEW_BTN,
        ),
        formid="%s_main_form" % prefix,
        counter=counter,
        with_loader=False,
    )


def get_supplier_invoice_all_form(request):
    """
    Return a void form used to export all non-exported supplier invoices

    :param obj counter: An iterator used for form id generation
    """
    schema = SupplierInvoiceAllSchema()
    schema = schema.bind(request=request)
    return deform.Form(
        schema=schema,
        buttons=(
            EXPORT_BTN,
            EXPORT_PREVIEW_BTN,
        ),
        formid="all_form",
        with_loader=False,
    )


def get_supplier_invoice_period_form(request, counter):
    """
    Return a form used to export supplier invoices from date to date
    :param obj counter: An iterator used for form id generation
    """
    schema = SupplierInvoicePeriodSchema()
    schema = schema.bind(request=request)
    return deform.Form(
        schema=schema,
        buttons=(
            EXPORT_BTN,
            EXPORT_PREVIEW_BTN,
        ),
        formid="period_form",
        counter=counter,
        with_loader=False,
    )


def get_supplier_invoice_form(request, counter):
    """
    Return a form for supplier invoice export
    :param obj request: Pyramid request object
    :returns: class:`deform.Form`

    """
    schema = SupplierInvoiceSchema()
    schema = schema.bind(request=request)
    return deform.Form(
        schema=schema,
        buttons=(
            EXPORT_BTN,
            EXPORT_PREVIEW_BTN,
        ),
        formid="main_form",
        counter=counter,
        with_loader=False,
    )


def get_supplier_invoice_number_form(request, counter, title):
    """
    Return a form for supplier invoice export by official_number
    :param counter: the iterator used to insert various forms in the same page
    """
    schema = SupplierInvoiceNumberSchema(title=title)
    schema = schema.bind(request=request)
    return deform.Form(
        schema=schema,
        buttons=(
            EXPORT_BTN,
            EXPORT_PREVIEW_BTN,
        ),
        formid="official_number_form",
        counter=counter,
        with_loader=False,
    )


def get_supplier_payment_all_form(request):
    """
    Return a void form used to export all non-exported documents

    """
    schema = SupplierPaymentAllSchema()
    schema = schema.bind(request=request)
    formid = "all_form"
    return deform.Form(
        schema=schema,
        buttons=(
            EXPORT_BTN,
            EXPORT_PREVIEW_BTN,
        ),
        formid=formid,
        with_loader=False,
    )


def get_supplier_payment_period_form(request, counter):
    """
    :param obj counter: An iterator used for form id generation
    """
    schema = SupplierPaymentPeriodSchema()
    schema = schema.bind(request=request)
    formid = "period_form"
    return deform.Form(
        schema=schema,
        buttons=(
            EXPORT_BTN,
            EXPORT_PREVIEW_BTN,
        ),
        formid=formid,
        counter=counter,
        with_loader=False,
    )


def get_supplier_payment_number_form(request, counter):
    """
    Return a form for supplier invoice export by official_number
    :param counter: the iterator used to insert various forms in the same page
    """
    schema = SupplierPaymentNumberSchema()
    schema = schema.bind(request=request)
    return deform.Form(
        schema=schema,
        buttons=(
            EXPORT_BTN,
            EXPORT_PREVIEW_BTN,
        ),
        formid="official_number_form",
        counter=counter,
        with_loader=False,
    )


def get_bpf_year_form(request, title, prefix="bpf"):
    """
    :param obj request: Pyramid request object
    :rtype: `deform.Form`
    :returns: a form for bpf export (agregate of BusinessBPFData)
    """
    schema = BPFYearSchema(title=title)
    schema = schema.bind(request=request, prefix=prefix)
    return deform.Form(
        schema=schema,
        buttons=(EXPORT_BTN,),
        formid="%s_main_form" % prefix,
        counter=0,
        with_loader=False,
    )


def format_export_type(db_export_type):
    if db_export_type == ACCOUNTING_EXPORT_TYPE_INVOICES:
        return "Factures"
    elif db_export_type == ACCOUNTING_EXPORT_TYPE_PAYMENTS:
        return "Encaissements"
    elif db_export_type == ACCOUNTING_EXPORT_TYPE_EXPENSES:
        return "Notes de dépenses"
    elif db_export_type == ACCOUNTING_EXPORT_TYPE_EXPENSE_PAYMENTS:
        return "Paiement de notes de dépenses"
    elif db_export_type == ACCOUNTING_EXPORT_TYPE_SUPPLIER_INVOICES:
        return "Factures fournisseur"
    elif db_export_type == ACCOUNTING_EXPORT_TYPE_SUPPLIER_PAYMENTS:
        return "Paiement de factures fournisseur"

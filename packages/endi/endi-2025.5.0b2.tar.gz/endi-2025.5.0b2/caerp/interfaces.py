from io import StringIO
from caerp.utils.compat import Iterable
from typing import (
    Dict,
    Union,
    List,
    Any,
)

from zope.interface import Interface
from zope.interface import Attribute


class IValidationStatusHolderService(Interface):
    """
    Interface for class that will produce collections of
    ValidationStatusHolderMixin implementors.
    """

    def waiting(*classes):
        """
        :return: iterable of instances implementing ValidationStatusHolderMixin
        """
        pass


class IValidationStateManager(Interface):
    """Interface for service class managing the states of a specific type"""

    def get_allowed_actions(request, context=None):
        """
        Return the list of next available actions regarding the
        current user's permissions
        """
        pass

    def check_allowed(action_name: str, context, request):
        """
        Check if the given action is allowed for the current user's permissions
        """
        pass

    def process(action_name: str, context, request, **params):
        """Process the action change"""
        pass


class IPaymentStateManager(IValidationStateManager):
    """Manage payment related states"""

    pass


class ISignedStateManager(IValidationStateManager):
    """Manage estimation signed status related states"""

    pass


class IJustifiedStateManager(IValidationStateManager):
    """Manage estimation signed status related states"""

    pass


class ITreasuryGroupper(Interface):
    """
    Groups several accounting operation lines together

    Instance can hold a state (settings), set via its constructor.
    """

    def group_items(items: Iterable[dict]) -> Iterable[dict]:
        """
        :param items: The items produced by the associated ITreasuryProducer
        """
        pass


class ITreasuryProducer(Interface):
    """
    Interface pour la production d'écriture comptable

    Produit des lignes sous la forme de dictionnaire qui vont être utilisées par les Writers
    """

    def get_item_entries(element: object):
        """
        Yield accounting operations for the given element
        """
        pass

    def get_book_entries(elements: Iterable[object]):
        """
        Yield accounting operations for the given elements
        """
        pass


class ITreasuryWriter(Interface):
    """
    Interface de base pour les différents modules de production de fichier
    d'écritures comptables
    Est également utilisé pour produire le preview des écritures
    """

    extension = Attribute("Filename extension csv, xls, txt ...")
    mimetype = Attribute(
        "Mimetype that will be used by enDI to describe the file type content"
    )
    headers = Attribute(
        "Iterable of python dict describing headers, should contain 'label' and 'name' and can also "
        "contain a 'typ' (text | date | number)"
    )

    def format_row(row) -> Union[List, dict]:
        """
        Format a model to a list of values or a dict regarding the type of export

        CSV : dict
        XLSX : list
        """
        pass

    def set_datas(lines: Iterable):
        """
        Set the tabular datas that will be written in the output file

        :param lines: The lines produced by the associated ITreasuryProducer
        """
        pass

    def format_cell(column_name, value):
        """
        Format the given row, method needed for previzualisation

        Writer classes in the sqla_inspect package provides such methods
        """
        pass

    def render() -> StringIO:
        """
        Produce the file data as a buffered file content like io.StringIO
        """
        pass


class ITreasuryInvoiceWriter(ITreasuryWriter):
    pass


class ITreasuryPaymentWriter(ITreasuryWriter):
    pass


class ITreasuryExpenseWriter(ITreasuryWriter):
    pass


class ITreasuryExpensePaymentWriter(ITreasuryWriter):
    pass


class ITreasurySupplierInvoiceWriter(ITreasuryWriter):
    pass


class ITreasurySupplierPaymentWriter(ITreasuryWriter):
    pass


class IFileRequirementService(Interface):
    """
    Describe the way a File Requirement service should work
    """

    def populate(node):
        """
        Populate the parent_object with File Requirements
        """
        pass

    def get_attached_indicators(node, file_type_id=None) -> list:
        """Return the indicators attached to the given node"""
        pass

    def get_related_indicators(node, file_type_id=None) -> list:
        """Return the indicators related to the given node (can be attached lower or
        higher in the hierarchy)"""
        pass

    def get_status(node) -> bool:
        """Returns the actual status of the node's related requirements"""
        pass

    def register(node, file_object, action="add"):
        """
        Register the file_object against the associated indicators
        """
        pass

    def force_all(node):
        """Force all requirement related to the given node"""
        pass

    def check_status(node):
        """Go throught related requirements and check if they should be updated"""
        pass


class IMoneyTask(Interface):
    """
    Interface for task handling money
    """

    def lines_total_ht():
        """
        Return the sum of the document lines
        """

    def total_ht():
        """
        return the HT total of the document
        """

    def discount_total_ht():
        """
        Return the HT discount
        """

    def get_tvas():
        """
        Return a dict with the tva amounts stored by tva reference
        """

    def tva_amount():
        """
        Return the amount of Tva to be paid
        """

    def total_ttc():
        """
        compute the ttc value before expenses
        """

    def total():
        """
        compute the total to be paid
        """

    def expenses_amount():
        """
        return the TTC expenses
        """


class IInvoice(Interface):
    """
    Invoice interface (used to get an uniform invoice list display
    See templates/invoices.mako (under invoice.model) to see the expected
    common informations
    """

    official_number = Attribute("""official number used in sage""")

    def total_ht():
        """
        Return the HT total of the current document
        """

    def tva_amount():
        """
        Return the sum of the tvas
        """

    def total():
        """
        Return the TTC total
        """

    def get_company():
        """
        Return the company this task is related to
        """

    def get_customer():
        """
        Return the customer this document is related to
        """


class IExporter(Interface):
    """
    Tabular exporter interface

    Some options can be passed by caller.
    Implementors MUST accept the options arguments but MAY ignore them

    DOCUMENT-LEVEL OPTIONS (`options` arg of add_row):

    - decimal_places (int, default 2) : how many decimals to display

    ROW-LEVEL OPTIONS (`options` arg of constructor):

    - highlight (bool, default False) : make the row visually outstand
    - hidden (bool, default False): hide the row, ideally keeping it in the document
    """

    def __init__(options: dict = None):
        pass

    def add_title(title: str, width: int, options: Dict[str, Any] = None):
        """
        Add a title to the spreadsheet

        :param title: The title to display
        :param width: On how many cells should the title be merged
        :param options: Options used to format the cells
        """
        pass

    def add_headers(headers: List[str]):
        """
        Add a header line to the file

        :param headers: Header labels
        """
        pass

    def add_row(row_datas, options: dict = None):
        """
        Add a row to the spreadsheet

        Implementor may or may not implement the following option keys
        - "hidden" (default False) : hide the row in the sheet.
        - "highlight" self.OPTION_HIGHLIGHT (default: False): highlight the row in the sheet

        :param list row_datas: The datas to display
        :param dict options: Key value options used to format the line
        """
        pass

    def render(f_buf=None):
        """
        Render the current spreadsheet to the given file buffer

        :param obj f_buf: File buffer (E.G file('....') or io.BytesIO
        """
        pass


class IPaymentRecordService(Interface):
    def add(user, invoice, params):
        """
        Record a new payment instance

        :param obj user: The User asking for recording
        :param obj invoice: The associated invoice object
        :param dict params: params used to generate the payment
        """
        pass

    def update(user, payment, params):
        """
        Modify an existing payment

        :param obj user: The User asking for recording
        :param obj invoice: The Payment object
        :param dict params: params used to generate the payment
        """
        pass

    def delete(user, payment):
        """
        Delete an existing payment

        :param obj user: The User asking for recording
        :param obj invoice: The Payment object
        """
        pass


class ITaskPdfRenderingService(Interface):
    """
    Service used to render invoice/estimation/cancelinvoice PDF
    including bulk rendering
    """

    def __init__(context, request):
        """
        :param obj context: The context that will be rendered
        :param obj request: The current Pyramid request
        """

    def set_task(task):
        """
        :param obj task: instance of Task that will replace the current context
        """

    def render_bulk(tasks):
        """
        Generates a pdf with the given tasks without the CGV pages

        :param list tasks: List of tasks to render
        :returns: A pdf buffer
        :rtype: :class:`io.BytesIO` instance
        """

    def render():
        """
        Generates a pdf output of the current context

        context and request are passed in the __init__ method of the service

        :returns: A pdf buffer
        :rtype: :class:`io.BytesIO` instance
        """

    def filename():
        """
        Generates a filename for the PDF output

        NB : a sale_pdf_filename_template is used in the configuration,
        the filename generation
        should use the keys described in the configuration

        :rtype: str
        """


class ITaskPdfStorageService(Interface):
    """
    Service used to persist invoice/estimation/cancelinvoice PDF datas on disk

    Persist the pdf datas if needed :

        When validated
        When rendered if valid and not stored
        When exported to treasury and not stored yet
    """

    def __init__(context, request):
        """
        :param obj context: The context that has been rendered
        :param obj request: The current Pyramid request
        """

    def set_task(task):
        """
        :param obj task: instance of Task that will replace the current context
        """

    def store_pdf(filename, pdf_buffer):
        """
        Store the generate pdf attached to the current context
        Handles all the data integrity stuff

        :param pdf_buffer: The Pdf buffer that should be store in database
        :type pdf_buffer: :class:`io.BytesIO` instance
        """

    def retrieve_pdf():
        """
        Retrieve the PDF associated to the current context or None if it's not
        stored yet
        :rtype: :class:`io.BytesIO` instance
        """


class IModuleRegistry(Interface):
    """
    Interface utilisée pour stocker les modules dans le registry pyramid
    """

    pass


class IPluginRegistry(Interface):
    """
    Interface utilisée pour stocker les plugins dans le registry pyramid
    """

    pass


class INotificationChannel(Interface):
    """
    Interface describing a notification channel
    (mail, caerp, sms, alert ...)
    """

    def __init__(context, request):
        """"""

    def send_to_user(notification, user, **kw):
        """Sends notification to a user

        :param notification: Notification to send
        :type notification: caerp.utils.notification.AbstractNotification
        :param user: The destination user
        :type user: User
        :param **kw: blindly forwarded channel custom parameters
        (like the source NotificationEvent for Notification models)
        """

    def send_to_company(notification, company, **kw):
        """Sends the notification to a company

        :param notification: Notification to send
        :type notification: caerp.utils.notification.AbstractNotification
        :param company: The destination company
        :type company: Company
        :param **kw: blindly forwarded channel custom parameters
        (like Attachment for emails)
        """


class IDataQueriesRegistry(Interface):
    """
    Interface utilisée pour stocker les requête statistiques dans le registre Pyramid
    """

    pass


class ISignPDFService(Interface):
    def sign(pdf_file_data):
        """
        Sign and timestamp PDF file

        :param obj pdf_file: The PDF file object
        """
        pass

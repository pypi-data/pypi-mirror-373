"""
Task rendering service

Base service used to render Task in PDF format
"""
import logging
from lxml.etree import (
    Element,
    SubElement,
    QName,
)
from facturx import generate_from_file
from PyPDF4 import PdfFileReader, PdfFileWriter
from PyPDF4.generic import Destination

from caerp.utils.ascii import force_filename
from caerp.models.task import (
    Task,
    Invoice,
    CancelInvoice,
    Estimation,
    InternalEstimation,
)
from caerp.compute import math_utils
from caerp.utils.html import strip_html_tags
from caerp.utils.strings import format_task_type


logger = logging.getLogger(__name__)


class TaskRawPdfFromHtmlService:
    """
    This class implements the
    :class:`caerp.interfaces.ITaskPdfRenderingService`

    """

    def __init__(self, context, request):
        self.context = context
        self.request = request
        if context is None:
            self.context = request.context

    def _get_config_option(self, option):
        value = self.request.config.get(option, " ")
        if not value:
            value = " "
        return value

    def render(self):
        """
        Render the current context in pdf format

        :rtype: instance of :class:`io.BytesIO`
        """
        logger.debug("Rendering PDF datas for {}".format(self.context))
        from caerp.export.task_pdf import task_pdf

        pdf_file = task_pdf(self.context, self.request)
        return pdf_file

    def filename(self):
        context_label = format_task_type(self.context)

        if self.context.status != "valid":
            number = "brouillon_{}".format(self.context.id)

        elif isinstance(self.context, (Estimation, InternalEstimation)):
            number = self.context.internal_number
        elif self.context.official_number:
            number = self.context.official_number
        else:
            raise Exception(
                "Should not happen {} is valid, not an estimation "
                "and yet has no official_number".format(self.context)
            )

        template = self._get_config_option("sale_pdf_filename_template")

        params = {
            "type_document": context_label.lower(),
            "numero": number,
            "client": self.context.customer.label.lower(),
            "enseigne": self.context.company.name.lower(),
            "cae": self._get_config_option("cae_business_name"),
        }
        # Pour le stockage en base du nom de fichier
        name = template.format(**params)[:250]
        return force_filename("{}.pdf".format(name))

    def set_task(self, task: Task):
        """
        :param obj task: instance of Task that will replace the current context
        """
        self.context = task


class TaskPdfFromHtmlService(TaskRawPdfFromHtmlService):
    """This class implements the
    :class:`caerp.interfaces.ITaskPdfRenderingService`

    It extends the TaskRawPdfFromHtmlService by adding FacturX
    information to the generated PDF.
    """

    def _get_facturx_xml(self):
        """
        Generates an XML output in Factur-X format with all invoice information

        :rtype: str
        """
        logger.debug("Generates Factur-X XML datas for {}".format(self.context))

        invoice = self.context
        invoice_type = "380"
        invoice_currency = "EUR"
        invoice_total_lines = 0
        invoice_total_discounts = 0

        class ns:
            qdt = "urn:un:unece:uncefact:data:standard:QualifiedDataType:100"
            ram = (
                "urn:un:unece:uncefact:data:standard:"
                "ReusableAggregateBusinessInformationEntity:100"
            )
            rsm = "urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100"
            udt = "urn:un:unece:uncefact:data:standard:UnqualifiedDataType:100"
            xsi = "http://www.w3.org/2001/XMLSchema-instance"

        fx_root = Element(
            QName(ns.rsm, "CrossIndustryInvoice"),
            nsmap={
                "qdt": ns.qdt,
                "ram": ns.ram,
                "rsm": ns.rsm,
                "udt": ns.udt,
                "xsi": ns.xsi,
            },
        )

        # BLOC IDENTIFICATION DU MESSAGE
        fx_child1 = SubElement(fx_root, QName(ns.rsm, "ExchangedDocumentContext"))
        fx_child2 = SubElement(
            fx_child1,
            QName(ns.ram, "GuidelineSpecifiedDocumentContextParameter"),
        )
        fx_child3 = SubElement(fx_child2, QName(ns.ram, "ID"))
        fx_child3.text = "urn:cen.eu:en16931:2017"

        # BLOC ENTETE DE MESSAGE
        fx_child1 = SubElement(fx_root, QName(ns.rsm, "ExchangedDocument"))
        fx_child2 = SubElement(fx_child1, QName(ns.ram, "ID"))
        fx_child2.text = invoice.official_number
        fx_child2 = SubElement(fx_child1, QName(ns.ram, "TypeCode"))
        fx_child2.text = invoice_type
        fx_child2 = SubElement(fx_child1, QName(ns.ram, "IssueDateTime"))
        fx_child3 = SubElement(fx_child2, QName(ns.udt, "DateTimeString"), format="102")
        fx_child3.text = invoice.date.strftime("%Y%m%d")
        if invoice.notes:
            fx_child2 = SubElement(fx_child1, QName(ns.ram, "IncludedNote"))
            fx_child3 = SubElement(fx_child2, QName(ns.ram, "Content"))
            fx_child3.text = invoice.notes

        # BLOC TRANSACTION COMMERCIALE
        fx_child1 = SubElement(fx_root, QName(ns.rsm, "SupplyChainTradeTransaction"))

        # LIGNES FACTURE
        line_number = 1
        for group in invoice.line_groups:
            for line in group.lines:
                line_pdt_name = strip_html_tags(line.description or "")
                # TODO : Récupérer le code de l'unité de la ligne
                line_unit_code = "C62"
                # TODO : Gérer les différents cas d'exo TVA
                line_tva_code = "E" if line.tva == 0 else "S"
                line_cost = math_utils.integer_to_amount(line.cost, 5)
                line_tva_rate = math_utils.integer_to_amount(line.tva, 2)
                line_total_amount = math_utils.integer_to_amount(line.total_ht(), 5)
                invoice_total_lines += line.total_ht()
                fx_child2 = SubElement(
                    fx_child1,
                    QName(ns.ram, "IncludedSupplyChainTradeLineItem"),
                )
                fx_child3 = SubElement(
                    fx_child2, QName(ns.ram, "AssociatedDocumentLineDocument")
                )
                fx_child4 = SubElement(fx_child3, QName(ns.ram, "LineID"))
                fx_child4.text = str(line_number)
                fx_child3 = SubElement(
                    fx_child2, QName(ns.ram, "SpecifiedTradeProduct")
                )
                fx_child4 = SubElement(fx_child3, QName(ns.ram, "Name"))
                fx_child4.text = line_pdt_name
                fx_child3 = SubElement(
                    fx_child2, QName(ns.ram, "SpecifiedLineTradeAgreement")
                )
                fx_child4 = SubElement(
                    fx_child3, QName(ns.ram, "GrossPriceProductTradePrice")
                )
                fx_child5 = SubElement(fx_child4, QName(ns.ram, "ChargeAmount"))
                fx_child5.text = str(line_cost)
                fx_child4 = SubElement(
                    fx_child3, QName(ns.ram, "NetPriceProductTradePrice")
                )
                fx_child5 = SubElement(fx_child4, QName(ns.ram, "ChargeAmount"))
                fx_child5.text = str(line_cost)
                fx_child3 = SubElement(
                    fx_child2, QName(ns.ram, "SpecifiedLineTradeDelivery")
                )
                fx_child4 = SubElement(
                    fx_child3,
                    QName(ns.ram, "BilledQuantity"),
                    unitCode=line_unit_code,
                )
                fx_child4.text = str(line.quantity)
                fx_child3 = SubElement(
                    fx_child2, QName(ns.ram, "SpecifiedLineTradeSettlement")
                )
                fx_child4 = SubElement(fx_child3, QName(ns.ram, "ApplicableTradeTax"))
                fx_child5 = SubElement(fx_child4, QName(ns.ram, "TypeCode"))
                fx_child5.text = "VAT"
                fx_child5 = SubElement(fx_child4, QName(ns.ram, "CategoryCode"))
                fx_child5.text = line_tva_code
                fx_child5 = SubElement(
                    fx_child4, QName(ns.ram, "RateApplicablePercent")
                )
                fx_child5.text = str(line_tva_rate)
                fx_child4 = SubElement(
                    fx_child3,
                    QName(ns.ram, "SpecifiedTradeSettlementLineMonetarySummation"),
                )
                fx_child5 = SubElement(fx_child4, QName(ns.ram, "LineTotalAmount"))
                fx_child5.text = str(line_total_amount)
                line_number += 1

        # TIERS
        fx_child2 = SubElement(
            fx_child1, QName(ns.ram, "ApplicableHeaderTradeAgreement")
        )
        # Vendeur
        fx_child3 = SubElement(fx_child2, QName(ns.ram, "SellerTradeParty"))
        fx_child4 = SubElement(fx_child3, QName(ns.ram, "Name"))
        fx_child4.text = self._get_config_option("cae_business_name")
        fx_child4 = SubElement(fx_child3, QName(ns.ram, "Description"))
        fx_child4.text = self._get_config_option("cae_legal_status")
        fx_child4 = SubElement(fx_child3, QName(ns.ram, "SpecifiedLegalOrganization"))
        fx_child5 = SubElement(fx_child4, QName(ns.ram, "ID"), schemeID="0002")
        fx_child5.text = self._get_config_option("cae_business_identification")
        fx_child5 = SubElement(fx_child4, QName(ns.ram, "TradingBusinessName"))
        fx_child5.text = invoice.company.name
        fx_child4 = SubElement(fx_child3, QName(ns.ram, "DefinedTradeContact"))
        fx_child5 = SubElement(fx_child4, QName(ns.ram, "PersonName"))
        fx_child5.text = invoice.company.name
        if invoice.company.phone or invoice.company.mobile:
            fx_child5 = SubElement(
                fx_child4, QName(ns.ram, "TelephoneUniversalCommunication")
            )
            fx_child6 = SubElement(fx_child5, QName(ns.ram, "CompleteNumber"))
            if invoice.company.phone:
                fx_child6.text = invoice.company.phone
            else:
                fx_child6.text = invoice.company.mobile
        if invoice.company.email:
            fx_child5 = SubElement(
                fx_child4, QName(ns.ram, "EmailURIUniversalCommunication")
            )
            fx_child6 = SubElement(fx_child5, QName(ns.ram, "URIID"), schemeID="SMTP")
            fx_child6.text = invoice.company.email
        fx_child4 = SubElement(fx_child3, QName(ns.ram, "PostalTradeAddress"))
        fx_child5 = SubElement(fx_child4, QName(ns.ram, "PostcodeCode"))
        fx_child5.text = self._get_config_option("cae_zipcode")
        cae_address = self._get_config_option("cae_address").splitlines()
        if len(cae_address) > 0:
            fx_child5 = SubElement(fx_child4, QName(ns.ram, "LineOne"))
            fx_child5.text = cae_address[0]
        if len(cae_address) > 1:
            fx_child5 = SubElement(fx_child4, QName(ns.ram, "LineTwo"))
            fx_child5.text = cae_address[1]
        if len(cae_address) > 2:
            fx_child5 = SubElement(fx_child4, QName(ns.ram, "LineThree"))
            fx_child5.text = cae_address[2]
        fx_child5 = SubElement(fx_child4, QName(ns.ram, "CityName"))
        fx_child5.text = self._get_config_option("cae_city")
        fx_child5 = SubElement(fx_child4, QName(ns.ram, "CountryID"))
        fx_child5.text = "FR"
        fx_child4 = SubElement(fx_child3, QName(ns.ram, "URIUniversalCommunication"))
        fx_child5 = SubElement(fx_child4, QName(ns.ram, "URIID"), schemeID="SMTP")
        fx_child5.text = self._get_config_option("cae_contact_email")
        fx_child4 = SubElement(fx_child3, QName(ns.ram, "SpecifiedTaxRegistration"))
        fx_child5 = SubElement(fx_child4, QName(ns.ram, "ID"), schemeID="VA")
        fx_child5.text = self._get_config_option("cae_intercommunity_vat")
        # Acheteur
        fx_child3 = SubElement(fx_child2, QName(ns.ram, "BuyerTradeParty"))
        fx_child4 = SubElement(fx_child3, QName(ns.ram, "Name"))
        fx_child4.text = invoice.customer.label
        if invoice.customer.type == "company":
            if invoice.customer.registration:
                fx_child4 = SubElement(
                    fx_child3, QName(ns.ram, "SpecifiedLegalOrganization")
                )
                fx_child5 = SubElement(fx_child4, QName(ns.ram, "ID"), schemeID="0002")
                fx_child5.text = invoice.customer.registration
            if invoice.customer.lastname:
                fx_child4 = SubElement(fx_child3, QName(ns.ram, "DefinedTradeContact"))
                fx_child5 = SubElement(fx_child4, QName(ns.ram, "PersonName"))
                fx_child5.text = "{} {}".format(
                    invoice.customer.lastname, invoice.customer.firstname
                )
        fx_child4 = SubElement(fx_child3, QName(ns.ram, "PostalTradeAddress"))
        fx_child5 = SubElement(fx_child4, QName(ns.ram, "PostcodeCode"))
        fx_child5.text = invoice.customer.zip_code

        buyer_address = invoice.customer.address
        if buyer_address:
            fx_child5 = SubElement(fx_child4, QName(ns.ram, "LineOne"))
            fx_child5.text = buyer_address
        additional_buyer_address = invoice.customer.additional_address.splitlines()
        if len(additional_buyer_address) > 0:
            fx_child5 = SubElement(fx_child4, QName(ns.ram, "LineTwo"))
            fx_child5.text = additional_buyer_address[0]
        if len(additional_buyer_address) > 1:
            fx_child5 = SubElement(fx_child4, QName(ns.ram, "LineThree"))
            fx_child5.text = additional_buyer_address[1]
        fx_child5 = SubElement(fx_child4, QName(ns.ram, "CityName"))
        fx_child5.text = invoice.customer.city
        fx_child5 = SubElement(fx_child4, QName(ns.ram, "CountryID"))
        fx_child5.text = "FR"  # TODO : Récupérer le code du pays du client
        fx_child4 = SubElement(fx_child3, QName(ns.ram, "URIUniversalCommunication"))
        fx_child5 = SubElement(fx_child4, QName(ns.ram, "URIID"), schemeID="SMTP")
        fx_child5.text = invoice.customer.email
        fx_child4 = SubElement(fx_child3, QName(ns.ram, "SpecifiedTaxRegistration"))
        fx_child5 = SubElement(fx_child4, QName(ns.ram, "ID"), schemeID="VA")
        fx_child5.text = invoice.customer.tva_intracomm

        # LIVRAISON (Obligatoire mais pas utilisé)
        fx_child2 = SubElement(
            fx_child1, QName(ns.ram, "ApplicableHeaderTradeDelivery")
        )

        # PAIEMENT
        fx_child2 = SubElement(
            fx_child1, QName(ns.ram, "ApplicableHeaderTradeSettlement")
        )
        fx_child3 = SubElement(fx_child2, QName(ns.ram, "PaymentReference"))
        fx_child3.text = invoice.official_number
        fx_child3 = SubElement(fx_child2, QName(ns.ram, "InvoiceCurrencyCode"))
        fx_child3.text = invoice_currency
        # Ventilation TVA
        invoice_ht_parts = invoice.tva_ht_parts()
        for tva, tva_amount in list(invoice.get_tvas().items()):
            # TODO : Gérer les différents cas d'exo TVA
            tva_code = "E" if tva == 0 else "S"
            tva_base_amount = math_utils.integer_to_amount(
                invoice_ht_parts.get(tva, 0), 5
            )
            tva_due_time_code = (
                "72"
                if self._get_config_option("cae_vat_collect_mode") == "encaissement"
                else "5"
            )
            tva_rate = math_utils.integer_to_amount(tva, 2)
            tva_amount = math_utils.integer_to_amount(tva_amount, 5)
            fx_child3 = SubElement(fx_child2, QName(ns.ram, "ApplicableTradeTax"))
            fx_child4 = SubElement(fx_child3, QName(ns.ram, "CalculatedAmount"))
            fx_child4.text = str(tva_amount)
            fx_child4 = SubElement(fx_child3, QName(ns.ram, "TypeCode"))
            fx_child4.text = "VAT"
            fx_child4 = SubElement(fx_child3, QName(ns.ram, "BasisAmount"))
            fx_child4.text = str(tva_base_amount)
            fx_child4 = SubElement(fx_child3, QName(ns.ram, "CategoryCode"))
            fx_child4.text = tva_code
            fx_child4 = SubElement(fx_child3, QName(ns.ram, "DueDateTypeCode"))
            fx_child4.text = tva_due_time_code
            fx_child4 = SubElement(fx_child3, QName(ns.ram, "RateApplicablePercent"))
            fx_child4.text = str(tva_rate)
        # Remises de la facture
        for discount in invoice.discounts:
            discount_amount = math_utils.integer_to_amount(discount.amount, 5)
            # TODO : Gérer les différents cas d'exo TVA
            discount_tva_code = "E" if discount.tva == 0 else "S"
            discount_tva_rate = math_utils.integer_to_amount(discount.tva, 2)
            discount_description = strip_html_tags(discount.description)
            fx_child3 = SubElement(
                fx_child2, QName(ns.ram, "SpecifiedTradeAllowanceCharge")
            )
            fx_child4 = SubElement(fx_child3, QName(ns.ram, "ChargeIndicator"))
            fx_child5 = SubElement(fx_child4, QName(ns.udt, "Indicator"))
            fx_child5.text = "false"
            fx_child4 = SubElement(fx_child3, QName(ns.ram, "ActualAmount"))
            fx_child4.text = str(discount_amount)
            fx_child4 = SubElement(fx_child3, QName(ns.ram, "Reason"))
            fx_child4.text = discount_description
            fx_child4 = SubElement(fx_child3, QName(ns.ram, "CategoryTradeTax"))
            fx_child5 = SubElement(fx_child4, QName(ns.ram, "TypeCode"))
            fx_child5.text = "VAT"
            fx_child5 = SubElement(fx_child4, QName(ns.ram, "CategoryCode"))
            fx_child5.text = discount_tva_code
            fx_child5 = SubElement(fx_child4, QName(ns.ram, "RateApplicablePercent"))
            fx_child5.text = str(discount_tva_rate)
        # Frais et charges de la facture
        if invoice.expenses_ht > 0:
            expenses_amount = math_utils.integer_to_amount(invoice.expenses_ht, 5)
            fx_child3 = SubElement(
                fx_child2, QName(ns.ram, "SpecifiedTradeAllowanceCharge")
            )
            fx_child4 = SubElement(fx_child3, QName(ns.ram, "ChargeIndicator"))
            fx_child5 = SubElement(fx_child4, QName(ns.udt, "Indicator"))
            fx_child5.text = "true"
            fx_child4 = SubElement(fx_child3, QName(ns.ram, "ActualAmount"))
            fx_child4.text = str(expenses_amount)
            fx_child4 = SubElement(fx_child3, QName(ns.ram, "CategoryTradeTax"))
            fx_child5 = SubElement(fx_child4, QName(ns.ram, "TypeCode"))
            fx_child5.text = "VAT"
            fx_child5 = SubElement(fx_child4, QName(ns.ram, "CategoryCode"))
            fx_child5.text = "S"
            fx_child5 = SubElement(fx_child4, QName(ns.ram, "RateApplicablePercent"))
            fx_child5.text = "20.0"
        # Conditions de paiement
        fx_child3 = SubElement(fx_child2, QName(ns.ram, "SpecifiedTradePaymentTerms"))
        fx_child4 = SubElement(fx_child3, QName(ns.ram, "Description"))
        fx_child4.text = invoice.payment_conditions
        fx_child4 = SubElement(fx_child3, QName(ns.ram, "DueDateDateTime"))
        fx_child5 = SubElement(fx_child4, QName(ns.udt, "DateTimeString"), format="102")
        # TODO : Calculer la date d'échéance
        fx_child5.text = invoice.date.strftime("%Y%m%d")
        # Totaux
        fx_child3 = SubElement(
            fx_child2,
            QName(ns.ram, "SpecifiedTradeSettlementHeaderMonetarySummation"),
        )
        fx_child4 = SubElement(fx_child3, QName(ns.ram, "LineTotalAmount"))
        fx_child4.text = str(math_utils.integer_to_amount(invoice_total_lines, 5))
        fx_child4 = SubElement(fx_child3, QName(ns.ram, "ChargeTotalAmount"))
        fx_child4.text = str(math_utils.integer_to_amount(invoice.expenses_ht, 5))
        fx_child4 = SubElement(fx_child3, QName(ns.ram, "AllowanceTotalAmount"))
        fx_child4.text = str(invoice_total_discounts)
        fx_child4 = SubElement(fx_child3, QName(ns.ram, "TaxBasisTotalAmount"))
        fx_child4.text = str(math_utils.integer_to_amount(invoice.ht, 5))
        fx_child4 = SubElement(
            fx_child3,
            QName(ns.ram, "TaxTotalAmount"),
            currencyID=invoice_currency,
        )
        fx_child4.text = str(math_utils.integer_to_amount(invoice.tva, 5))
        fx_child4 = SubElement(fx_child3, QName(ns.ram, "GrandTotalAmount"))
        fx_child4.text = str(math_utils.integer_to_amount(invoice.ttc, 5))
        fx_child4 = SubElement(fx_child3, QName(ns.ram, "DuePayableAmount"))
        fx_child4.text = str(math_utils.integer_to_amount(invoice.ttc, 5))
        # Référence à une facture antérieure
        if hasattr(invoice, "invoice"):
            fx_child3 = SubElement(
                fx_child2, QName(ns.ram, "InvoiceReferencedDocument")
            )
            fx_child4 = SubElement(fx_child3, QName(ns.ram, "IssuerAssignedID"))
            fx_child4.text = invoice.invoice.official_number
        return fx_root

    def _collect_outlines(self, pdf_file):
        """
        Collect the first level outlines of the given pdf document

        :param obj pdf_file: A buffer containing the generated pdf
        :returns: A list of 2-uple [(title, destination_page)]
        """
        reader = PdfFileReader(pdf_file)
        toctree = []
        for outline in reader.getOutlines():
            if isinstance(outline, Destination):
                page = reader.getDestinationPageNumber(outline)
                toctree.append((outline.title, page))
        return toctree

    def _restore_outlines(self, pdf_file, toctree):
        """
        Restore the outlines of the original document into the pdf generated by
        facturex
        """
        writer = PdfFileWriter()
        reader = PdfFileReader(pdf_file)

        # Here we copy the data from the facturex populated pdf file to the
        # writer before adding bookmarks
        # NOTE: PyPDF4 clone methods doesn't work as is, this is a solution
        # that work
        writer.cloneReaderDocumentRoot(reader)
        for rpagenum in range(0, reader.getNumPages()):
            writer.addPage(reader.getPage(rpagenum))

        # Add the bookmarks
        for title, page in toctree:
            writer.addBookmark(title, page)
        writer.write(pdf_file)
        return writer

    def render(self):
        """
        Render the current context in pdf format

        :rtype: instance of :class:`io.BytesIO`
        """
        pdf_file = super().render()
        if (
            isinstance(self.context, (Invoice, CancelInvoice))
            and self.context.status == "valid"
        ):
            # NOTE:
            # store the bookmarks (outlines) of the generated pdf to restore it
            # after generating facturx pdf file
            # See https://github.com/akretion/factur-x/issues/20
            outlines = self._collect_outlines(pdf_file)
            xml = self._get_facturx_xml()
            generate_from_file(pdf_file, xml, flavor="factur-x")
            self._restore_outlines(pdf_file, outlines)

        return pdf_file

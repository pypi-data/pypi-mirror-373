"""
Outil de production de fichier XML de virement SEPA

Pour tester les fichiers en version pain.001.001.3 :
https://www.mesfluxdepaiement.fr/testez-vos-fichiers-sepa/
"""
import datetime
import logging
import os

import schwifty
from lxml import etree

from caerp.utils.ascii import force_ascii
from caerp.utils.strings import get_random_string, integer_to_decimal_string

from .abstract import AbstractPayment, Creditor, Debtor

# Set up logging
logger = logging.getLogger(__name__)


def _get_message_id():
    random_root = get_random_string(12)
    return f"{random_root}-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"


def force_ascii_strings(text):
    return "".join([a for a in force_ascii(text) if a.isalpha() or a.isdigit()])


class SepaCreditTransferXmlFactory:
    """
    Tool used to produce XML credit transfer files for SEPA
    """

    DEFAULT_VERSION = "001.001.09"

    SUPPORTED_VERSIONS = {
        "001.001.03": "urn:iso:std:iso:20022:tech:xsd:pain.001.001.03",
        "001.001.05": "urn:iso:std:iso:20022:tech:xsd:pain.001.001.05",
        "001.001.09": "urn:iso:std:iso:20022:tech:xsd:pain.001.001.09",
    }

    def __init__(self, debtor: Debtor, execution_date=None, pain_version="001.001.03"):
        self.debtor = debtor
        self.execution_date = (
            execution_date if execution_date else datetime.date.today()
        )

        self.payments = []
        if pain_version not in self.SUPPORTED_VERSIONS:
            raise ValueError(
                f"Unsupported PAIN version. "
                f"Supported versions are: {', '.join(self.SUPPORTED_VERSIONS.keys())}"
            )
        self.pain_version = pain_version
        self.msg_id = _get_message_id()
        logger.info(
            f"Initialized SepaCreditTransferXmlFactory with PAIN version {pain_version}"
        )

    def get_msg_id(self):
        """
        Return the unique message identification for this SEPA Transfer
        """
        return self.msg_id

    def add_payment(self, payment: AbstractPayment):
        """
        Add a payment to the current SEPA Transfer object

        You should specify

            an amount
            a transfer_ref
            the creditor's details
        """
        self.payments.append(payment)
        logger.info(f"Added payment: {payment.amount} to {payment.creditor.name}")

    def _add_address(self, parent, address, country):
        pstl_adr = etree.SubElement(parent, "PstlAdr")
        etree.SubElement(pstl_adr, "Ctry").text = country
        for line in address.split("\n"):
            etree.SubElement(pstl_adr, "AdrLine").text = force_ascii_strings(line)

    def validate_xml(self, xml_string):
        """
        Run xml validation regarding the current SEPA PAIN schema
        """
        schema_path = os.path.join(
            os.path.dirname(__file__), "schemas", f"pain.{self.pain_version}.xsd"
        )
        if not os.path.exists(schema_path):
            logger.error(f"Missing pain xsd schema not found at {schema_path}")
            raise FileNotFoundError(f"Schema not found at {schema_path}")

        xmlschema_doc = etree.parse(schema_path)
        xmlschema = etree.XMLSchema(xmlschema_doc)

        xml_doc = etree.fromstring(xml_string)
        is_valid = xmlschema.validate(xml_doc)

        if not is_valid:
            errors = xmlschema.error_log
            logger.error(f"XML validation errors: {errors}")
            raise ValueError(f"Invalid XML: {errors}")
        else:
            logger.info("XML validation successful")

    def add_group_header(self, cstmr_cdt_trf_initn, total_payment):
        """
        Add the <GrpHdr> node to the <CstmrCdtTrfInitn> node
        """
        grp_hdr = etree.SubElement(cstmr_cdt_trf_initn, "GrpHdr")
        etree.SubElement(grp_hdr, "MsgId").text = self.msg_id
        etree.SubElement(grp_hdr, "CreDtTm").text = datetime.datetime.now().isoformat()
        etree.SubElement(grp_hdr, "NbOfTxs").text = str(len(self.payments))
        etree.SubElement(grp_hdr, "CtrlSum").text = integer_to_decimal_string(
            total_payment
        )

        initg_pty = etree.SubElement(grp_hdr, "InitgPty")
        etree.SubElement(initg_pty, "Nm").text = force_ascii(self.debtor.name)

    def add_debtor_node(self, pmt_inf):
        """
        Add xml nodes describing the debtor details (CAE in this case)

        <PmtInf>
            <Dbtr>
            ...
            </Dbtr>
        </PmtInf>
        """
        dbtr = etree.SubElement(pmt_inf, "Dbtr")
        etree.SubElement(dbtr, "Nm").text = force_ascii(self.debtor.name)

        # À priori l'adresse n'est pas obligatoire, on s'en passe
        # self._add_address(dbtr, self.debtor.address, self.debtor.country)

        dbtr_acct = etree.SubElement(pmt_inf, "DbtrAcct")
        id_element = etree.SubElement(dbtr_acct, "Id")
        etree.SubElement(id_element, "IBAN").text = self.debtor.iban

        dbtr_agt = etree.SubElement(pmt_inf, "DbtrAgt")
        fin_instn_id = etree.SubElement(dbtr_agt, "FinInstnId")
        if self.pain_version == "001.001.09":
            other = etree.SubElement(fin_instn_id, "Othr")
            etree.SubElement(other, "Id").text = self.debtor.bic
        elif self.pain_version == "001.001.05":
            etree.SubElement(fin_instn_id, "BICFI").text = self.debtor.bic
        else:
            etree.SubElement(fin_instn_id, "BIC").text = self.debtor.bic

        etree.SubElement(pmt_inf, "ChrgBr").text = "SLEV"

    def add_main_transfer_informations(self, cstmr_cdt_trf_initn, total_payment):
        """
        Add the main informations of the <PmtInf> node

            transfer id
            transfer due date
            ...
            debtor : <Dbtr>...</Dbtr>
        """
        # Code du paiement
        pmt_inf = etree.SubElement(cstmr_cdt_trf_initn, "PmtInf")
        etree.SubElement(
            pmt_inf, "PmtInfId"
        ).text = f'PMT-{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}'
        etree.SubElement(pmt_inf, "PmtMtd").text = "TRF"

        # On veut une ligne par virement dans le compte bancaire
        etree.SubElement(pmt_inf, "BtchBookg").text = "false"
        etree.SubElement(pmt_inf, "NbOfTxs").text = str(len(self.payments))
        etree.SubElement(pmt_inf, "CtrlSum").text = integer_to_decimal_string(
            total_payment
        )

        pmt_tp_inf = etree.SubElement(pmt_inf, "PmtTpInf")
        svc_lvl = etree.SubElement(pmt_tp_inf, "SvcLvl")
        etree.SubElement(svc_lvl, "Cd").text = "SEPA"
        # Date d'exécution
        if self.pain_version == "001.001.09":
            reqd_exctn_dt = etree.SubElement(pmt_inf, "ReqdExctnDt")
            etree.SubElement(reqd_exctn_dt, "Dt").text = self.execution_date.strftime(
                "%Y-%m-%d"
            )
        else:
            etree.SubElement(
                pmt_inf, "ReqdExctnDt"
            ).text = self.execution_date.strftime("%Y-%m-%d")

        self.add_debtor_node(pmt_inf)
        return pmt_inf

    def add_payment_xml(self, pmt_inf, payment: AbstractPayment):
        """
        Add a <CdtTrfTxInf> node to the <PmtInf> node

        <CdtTrfTxInf> represents a single payment
        """
        cdt_trf_tx_inf = etree.SubElement(pmt_inf, "CdtTrfTxInf")
        pmt_id = etree.SubElement(cdt_trf_tx_inf, "PmtId")
        etree.SubElement(
            pmt_id, "EndToEndId"
        ).text = f'E2E-{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}'

        amt = etree.SubElement(cdt_trf_tx_inf, "Amt")
        etree.SubElement(
            amt, "InstdAmt", attrib={"Ccy": "EUR"}, nsmap={}
        ).text = integer_to_decimal_string(payment.amount)

        cdtr_agt = etree.SubElement(cdt_trf_tx_inf, "CdtrAgt")
        fin_instn_id = etree.SubElement(cdtr_agt, "FinInstnId")
        if self.pain_version == "001.001.09":
            other = etree.SubElement(fin_instn_id, "Othr")
            etree.SubElement(other, "Id").text = payment.creditor.bic
        elif self.pain_version == "001.001.05":
            etree.SubElement(fin_instn_id, "BICFI").text = payment.creditor.bic
        else:
            etree.SubElement(fin_instn_id, "BIC").text = payment.creditor.bic

        cdtr = etree.SubElement(cdt_trf_tx_inf, "Cdtr")
        etree.SubElement(cdtr, "Nm").text = force_ascii(payment.creditor.name)
        # self._add_address(cdtr, payment.creditor.address, payment.creditor.country)

        cdtr_acct = etree.SubElement(cdt_trf_tx_inf, "CdtrAcct")
        id_element = etree.SubElement(cdtr_acct, "Id")
        etree.SubElement(id_element, "IBAN").text = payment.creditor.iban

        rmt_inf = etree.SubElement(cdt_trf_tx_inf, "RmtInf")
        etree.SubElement(rmt_inf, "Ustrd").text = force_ascii_strings(
            payment.transfer_ref
        )

    def generate_xml(self, pretty_print=False):
        """
        Generate the sepa XML in the expected PAIN format
        """
        nsmap = {None: self.SUPPORTED_VERSIONS[self.pain_version]}
        root = etree.Element("Document", nsmap=nsmap)
        cstmr_cdt_trf_initn = etree.SubElement(root, "CstmrCdtTrfInitn")
        total_payment = sum((payment.amount for payment in self.payments))

        # Group Header
        self.add_group_header(cstmr_cdt_trf_initn, total_payment)

        # Payment Information
        pmt_inf = self.add_main_transfer_informations(
            cstmr_cdt_trf_initn, total_payment
        )

        for payment in self.payments:
            self.add_payment_xml(pmt_inf, payment)

        xml_string = etree.tostring(root, xml_declaration=True, encoding="UTF-8")
        if pretty_print:
            from xml.dom import minidom

            out_minidom = minidom.parseString(xml_string)
            xml_string = out_minidom.toprettyxml(encoding="UTF-8")

        # Log the generated XML
        logger.debug(
            f"Generated XML for PAIN version {self.pain_version}:\n{xml_string}"
        )

        # Validate the generated XML
        self.validate_xml(xml_string)

        return xml_string


# Usage example
if __name__ == "__main__":
    """
    Lancer python -m caerp.utils.sepa.credit_transfer pour produire des
    fichiers de tests
    """
    for version in SepaCreditTransferXmlFactory.SUPPORTED_VERSIONS.keys():
        logger.info(f"Generating XML for PAIN version {version}")
        sepa = SepaCreditTransferXmlFactory(
            Debtor(name="Entreprise méritante", iban=str(schwifty.IBAN.random("FR"))),
            pain_version=version,
        )
        entrepreneur = Creditor(
            name="Jérôme Maçon", iban=str(schwifty.IBAN.random("FR"))
        )
        sepa.add_payment(
            AbstractPayment(
                amount=10000,
                transfer_ref="Note de dépenses mars 2025",
                creditor=entrepreneur,
            )
        )
        sepa.add_payment(
            AbstractPayment(
                amount=10256,
                transfer_ref="Note de dépenses avril 2025",
                creditor=entrepreneur,
            )
        )
        fournisseur = Creditor(
            name="étoile & lune", iban=str(schwifty.IBAN.random("FR"))
        )
        sepa.add_payment(
            AbstractPayment(
                amount=20000, transfer_ref="Invoice 456", creditor=fournisseur
            )
        )

        try:
            xml_content = sepa.generate_xml(pretty_print=True)
            logger.info(f"XML for PAIN version {version} is valid.")

            # Optionally, save to a file
            with open(f"sepa_credit_transfer_{version}.xml", "wb") as f:
                f.write(xml_content)
            logger.info(f"XML file saved: sepa_credit_transfer_{version}.xml")
        except ValueError as e:
            logger.error(f"XML validation failed for PAIN version {version}: {e}")

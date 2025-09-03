from zope.interface import implementer

from caerp.interfaces import ITreasuryProducer

from caerp.compute.sage.invoice import (
    InternalInvoiceExportProducer,
    InvoiceExportProducer,
    CustomBookEntryFactory,
)
from caerp.compute.sage.expense import (
    SageExpenseMain,
    ExpenseExportProducer,
)
from caerp.compute.sage.payment import (
    InternalPaymentExportProducer,
    PaymentExportProducer,
)
from caerp.compute.sage.supplier_invoice import (
    SupplierInvoiceExportProducer,
)

import logging

logger = logging.getLogger(__name__)


class CustomFactory(CustomBookEntryFactory):
    def credit_company(self):
        gen_entry, analytic_entry = super().credit_company()
        # Spécifique à une des deux CAE (qui est la seule des deux
        # à utiliser le module de contribution)
        analytic_entry["compte_cg"] = "461219100"
        logger.debug(gen_entry)
        logger.debug(analytic_entry)
        return gen_entry, analytic_entry


# VENTES
@implementer(ITreasuryProducer)
class InvoiceProducer(InvoiceExportProducer):
    """
    Custom producer pour les factures
    c'est lui qui produit les lignes d'export pour les factures
    ici il s'assure de vire une des deux lignes analytiques/générales
    """

    use_general = False
    _available_modules = {}
    _custom_factory = CustomFactory


@implementer(ITreasuryProducer)
class InternalInvoiceProducer(InternalInvoiceExportProducer):
    use_general = False
    _available_modules = {}


@implementer(ITreasuryProducer)
class PaymentProducer(PaymentExportProducer):
    use_general = False


@implementer(ITreasuryProducer)
class InternalPaymentProducer(InternalPaymentExportProducer):
    use_general = False


# NDD
@implementer(ITreasuryProducer)
class ExpenseProducer(ExpenseExportProducer):
    _default_modules = (SageExpenseMain,)
    use_general = False


# FOURNISSEURS
@implementer(ITreasuryProducer)
class SupplierInvoiceProducer(SupplierInvoiceExportProducer):
    use_general = False


@implementer(ITreasuryProducer)
class InternalSupplierInvoiceProducer(SupplierInvoiceExportProducer):
    use_general = False

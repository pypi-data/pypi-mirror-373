import logging

from sqlalchemy import inspect
from zope.interface import implementer

from caerp.compute.math_utils import translate_integer_precision
from caerp.interfaces import IPaymentRecordService

logger = logging.getLogger(__name__)


# Service au sens de pyramid_services
@implementer(IPaymentRecordService)
class InternalPaymentRecordService:
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.dbsession = request.dbsession

    def add(self, invoice, params):
        """
        Record a new payment instance

        :param obj user: The User asking for recording
        :param obj invoice: The associated invoice object
        :param dict params: params used to generate the payment
        """
        from caerp.models.task import InternalInvoice, InternalPayment

        if not isinstance(invoice, InternalInvoice):
            raise Exception("{} is not an InternalInvoice".format(invoice))
        supplier_invoice = invoice.supplier_invoice
        if supplier_invoice is None:
            supplier_invoice = invoice.sync_with_customer(self.request)

        logger.info(
            "{} is adding an InternalPayment for InternalInvoice {}".format(
                self.request.identity.id, invoice.id
            )
        )
        payment = InternalPayment()
        mapper = inspect(InternalPayment)
        columns = (i.key for i in mapper.attrs)
        for key, value in params.items():
            if key in columns:
                print(key, value)
                setattr(payment, key, value)
                print("Done")

        payment.user = self.request.identity

        invoice.payments.append(payment)
        self.dbsession.merge(invoice)
        payment.sync_with_customer(self.request, action="add")
        return payment

    def update(self, payment, params):
        """
        Modify an existing payment

        :param obj user: The User asking for recording
        :param obj invoice: The Payment object
        :param dict params: params used to generate the payment
        """
        from caerp.models.task import InternalPayment

        if not isinstance(payment, InternalPayment):
            raise Exception("{} is not an InternalPayment".format(payment))

        old_amount = payment.amount
        logger.info(
            "{} is updating the InternalPayment {} for "
            "InternalInvoice {}".format(
                self.request.identity.id, payment.id, payment.task_id
            )
        )
        for key, value in params.items():
            setattr(payment, key, value)

        self.dbsession.merge(payment)
        self.dbsession.flush()
        payment.sync_with_customer(self.request, action="update", amount=old_amount)
        return payment

    def delete(self, payment):
        """
        Delete an existing payment

        :param obj payment: The InternalPayment instance to delete

        :returns: True/False if the deletion succeeded
        :rtype: bool
        """
        from caerp.models.task import InternalPayment

        if not isinstance(payment, InternalPayment):
            raise Exception("{} is not an InternalPayment".format(payment))
        old_amount = payment.amount
        logger.info(
            "{} is deleting the InternalPayment {} for "
            "InternalInvoice {}".format(
                self.request.identity.id, payment.id, payment.task_id
            )
        )
        self.dbsession.delete(payment)
        self.dbsession.flush()

        payment.sync_with_customer(self.request, action="delete", amount=old_amount)


class InternalPaymentService:
    @classmethod
    def sync_with_customer(cls, payment, request, action="add", **kw):
        logger.info(
            f" + Syncing internal invoice's payment with associated supplier_invoice. "
            f"Action {action} payment id : "
            f"{payment.id}"
        )
        supplier_invoice = payment.invoice.supplier_invoice
        force_resulted = payment.invoice.paid_status == "resulted"

        from caerp.controllers.payment import record_payment

        # Avoid circular imports
        from caerp.controllers.state_managers import (
            check_node_resulted,
            set_validation_status,
        )
        from caerp.models.supply.internalpayment import (
            InternalSupplierInvoiceSupplierPayment,
        )

        amount = translate_integer_precision(payment.amount, 5, 2)
        if action == "add":
            if not supplier_invoice.status == "valid":
                set_validation_status(request, supplier_invoice, "valid")

            supplier_payment = InternalSupplierInvoiceSupplierPayment(
                amount=amount,
                date=payment.date,
            )
            record_payment(
                request,
                supplier_invoice,
                supplier_payment,
            )
            check_node_resulted(
                request,
                supplier_invoice,
                force_resulted=force_resulted,
            )
            request.dbsession.merge(supplier_invoice)
            request.dbsession.flush()
            return supplier_payment
        else:
            old_amount = translate_integer_precision(kw["amount"], 5, 2)
            # On retrouve le InternalSupplierInvoiceSupplierPayment associé
            supplier_payment = (
                InternalSupplierInvoiceSupplierPayment.query()
                .filter_by(
                    supplier_invoice_id=supplier_invoice.id,
                    amount=old_amount,
                )
                .first()
            )
            if not supplier_payment:
                logger.warning(
                    "Unable to find an InternalSupplierInvoiceSupplierPayment "
                    "(supplier_invoice {}) associated to the Payment {} "
                    "(invoice {})".format(supplier_invoice, payment, payment.invoice)
                )
            elif action == "update":
                supplier_payment.amount = amount
                supplier_payment.date = payment.date
                request.dbsession.merge(supplier_payment)
                request.dbsession.flush()

            else:
                supplier_invoice.payments.remove(supplier_payment)
                request.dbsession.merge(supplier_invoice)
                request.dbsession.flush()

            check_node_resulted(
                request, supplier_invoice, force_resulted=force_resulted
            )
            request.dbsession.merge(supplier_invoice)
            return supplier_payment

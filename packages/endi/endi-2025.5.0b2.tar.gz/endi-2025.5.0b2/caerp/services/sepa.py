from typing import List, Optional, Union

import schwifty
from sqlalchemy import func, select

from caerp.exception import MissingConfigError
from caerp.models.expense.sheet import ExpenseSheet
from caerp.models.payments import BankAccount
from caerp.models.sepa import (
    BaseSepaWaitingPayment,
    ExpenseSepaWaitingPayment,
    SepaCreditTransfer,
    SupplierInvoiceSupplierSepaWaitingPayment,
    SupplierInvoiceUserSepaWaitingPayment,
)
from caerp.models.supply.supplier_invoice import SupplierInvoice
from caerp.models.third_party import ThirdParty
from caerp.models.user import User
from caerp.services.config import get_cae_name
from caerp.utils.sepa.abstract import AbstractPayment, Creditor, Debtor
from caerp.utils.sepa.credit_transfer import SepaCreditTransferXmlFactory


def third_party_to_creditor(third_party: ThirdParty) -> Creditor:
    """
    Convert a ThirdParty to a Creditor object
    """
    return Creditor(
        name=third_party.name,
        iban=third_party.bank_account_iban,
        bic=third_party.bank_account_bic,
    )


def user_to_creditor(user: User) -> Creditor:
    """
    Convert a user to a Creditor object
    """

    return Creditor(
        name=user.bank_account_owner,
        iban=user.bank_account_iban,
        bic=user.bank_account_bic,
    )


def get_cae_debtor(request, bank_account: BankAccount) -> Debtor:
    """
    Create a Debtor object from BankAccount + cae config data
    """
    name = get_cae_name(request)

    if not name:
        raise MissingConfigError(
            message="Le nom de la CAE n'a pas été configuré",
        )

    iban = bank_account.iban
    if not iban:
        raise MissingConfigError(
            message="L'IBAN du compte bancaire de la CAE n'a pas été configuré",
        )
    bic = bank_account.bic
    assert is_valid_iban(iban), "L'IBAN du compte bancaire de la CAE n'est pas valide"
    assert is_valid_bic(bic), "Le BIC du compte bancaire de la CAE n'est pas valide"
    return Debtor(name=name, iban=iban, bic=bic)


def waiting_payment_to_abstract_payment(
    request,
    waiting_payment: Union[
        ExpenseSepaWaitingPayment,
        SupplierInvoiceSupplierSepaWaitingPayment,
        SupplierInvoiceUserSepaWaitingPayment,
    ],
) -> AbstractPayment:
    if isinstance(waiting_payment, ExpenseSepaWaitingPayment):
        return expense_waiting_payment_to_abstract_payment(request, waiting_payment)
    elif isinstance(waiting_payment, SupplierInvoiceSupplierSepaWaitingPayment):
        return supplier_waiting_payment_to_abstract_payment(request, waiting_payment)
    else:
        return user_waiting_payment_to_abstract_payment(request, waiting_payment)


def expense_waiting_payment_to_abstract_payment(
    request, waiting_payment: ExpenseSepaWaitingPayment
) -> AbstractPayment:
    """
    Convert an expense sheet waiting payment to an AbstractPayment object
    """
    assert waiting_payment.amount > 0, "Le montant du paiement doit être supérieur à 0"
    expense_sheet = waiting_payment.expense_sheet
    can_expense_sheet_be_paid(request, expense_sheet)
    creditor = user_to_creditor(waiting_payment.expense_sheet.user)
    return AbstractPayment(
        amount=waiting_payment.amount,
        transfer_ref=f"NDD {expense_sheet.official_number}",
        creditor=creditor,
    )


def supplier_waiting_payment_to_abstract_payment(
    request, waiting_payment: SupplierInvoiceSupplierSepaWaitingPayment
):
    """
    Convert a supplier invoice to an AbstractPayment object
    """
    supplier_invoice = waiting_payment.supplier_invoice
    can_supplier_be_paid(request, supplier_invoice)
    assert waiting_payment.amount > 0, "Le montant du paiement doit être supérieur à 0"
    return AbstractPayment(
        amount=waiting_payment.amount,
        transfer_ref=f"Facture {supplier_invoice.remote_invoice_number}",
        creditor=third_party_to_creditor(supplier_invoice.supplier),
    )


def user_waiting_payment_to_abstract_payment(
    request, waiting_payment: SupplierInvoiceUserSepaWaitingPayment
):
    """
    Convert a SupplierInvoiceUserSepaWaitingPayment to an AbstractPayment object
    """
    supplier_invoice = waiting_payment.supplier_invoice
    can_user_be_paid(request, supplier_invoice)
    assert waiting_payment.amount > 0, "Le montant du paiement doit être supérieur à 0"
    return AbstractPayment(
        amount=waiting_payment.amount,
        transfer_ref=f"Facture {supplier_invoice.remote_invoice_number}",
        creditor=user_to_creditor(supplier_invoice.payer),
    )


def can_supplier_be_paid(request, supplier_invoice: SupplierInvoice) -> bool:
    assert (
        supplier_invoice.cae_topay() > 0
    ), "Il ne reste rien à rembourser au fournisseur"
    supplier = supplier_invoice.supplier
    assert is_valid_iban(
        supplier.bank_account_iban
    ), "L'IBAN du fournisseur doit être renseigné"
    assert is_valid_bic(
        supplier.bank_account_bic
    ), "Le BIC du fournisseur doit être renseigné"
    return True


def can_user_be_paid(request, supplier_invoice: SupplierInvoice) -> bool:
    assert (
        supplier_invoice.worker_topay() > 0
    ), "Il ne reste rien à rembourser à l'entrepreneur"
    user = supplier_invoice.payer
    assert is_valid_iban(
        user.bank_account_iban
    ), "L'IBAN du compte bancaire de l'utilisateur doit être renseigné"
    assert is_valid_bic(
        user.bank_account_bic
    ), "Le BIC du compte bancaire de l'utilisateur doit être renseigné"
    return True


def can_expense_sheet_be_paid(request, expense_sheet: ExpenseSheet) -> bool:
    assert expense_sheet.topay() > 0, "Le montant à payer est à 0"
    assert is_valid_iban(
        expense_sheet.user.bank_account_iban
    ), "L'IBAN du compte bancaire de l'utilisateur doit être renseigné"
    assert is_valid_bic(
        expense_sheet.user.bank_account_bic
    ), "Le BIC du compte bancaire de l'utilisateur doit être renseigné"
    return True


def get_open_sepa_credit_transfer(request) -> Optional[SepaCreditTransfer]:
    """
    Retourne l'ordre de virement SEPA en cours d'édition
    """
    return request.dbsession.execute(
        select(SepaCreditTransfer).where(
            SepaCreditTransfer.status == SepaCreditTransfer.OPEN_STATUS
        )
    ).scalar()


def is_valid_iban(iban):
    if not iban:
        return False
    try:
        schwifty.IBAN(iban, validate_bban=True)
    except schwifty.exceptions.SchwiftyException:
        return False
    else:
        return True


def is_valid_bic(bic):
    if not bic:
        return False
    try:
        schwifty.BIC(bic)
    except schwifty.exceptions.SchwiftyException:
        return False
    else:
        return True


def has_waiting_payments(request) -> bool:
    """
    Check if there are any waiting payments
    """
    query = select(func.count(BaseSepaWaitingPayment.id)).filter(
        BaseSepaWaitingPayment.paid_status == BaseSepaWaitingPayment.WAIT_STATUS
    )
    return request.dbsession.execute(query).scalar() > 0


def get_available_sepa_pain_versions() -> List[str]:
    versions = list(SepaCreditTransferXmlFactory.SUPPORTED_VERSIONS.keys())
    versions.sort()
    return versions

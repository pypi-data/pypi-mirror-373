import colander
import deform
from sqlalchemy import select

from caerp import forms
from caerp.models.payments import Bank, BankAccount, PaymentMode


def get_payment_mode_options(request):
    return request.dbsession.execute(
        select(PaymentMode.label, PaymentMode.label).order_by(PaymentMode.order)
    ).all()


def get_payment_mode_default(request):
    return request.dbsession.execute(
        select(PaymentMode.label).order_by(PaymentMode.order)
    ).scalar()


@colander.deferred
def deferred_payment_mode_widget(node, kw):
    """
    dynamically retrieves the payment modes
    """
    return deform.widget.SelectWidget(values=get_payment_mode_options(kw["request"]))


def get_payment_mode_validator(request):
    elements = request.dbsession.execute(select(PaymentMode.label)).scalars().all()
    return colander.OneOf(elements)


@colander.deferred
def deferred_payment_mode_validator(node, kw):
    return get_payment_mode_validator(kw["request"])


def get_bank_account_options(request):
    return request.dbsession.execute(
        select(BankAccount.id, BankAccount.label)
        .where(BankAccount.active.is_(True))
        .order_by(BankAccount.default.desc(), BankAccount.order)
    ).all()


@colander.deferred
def deferred_bank_account_widget(node, kw):
    """
    Renvoie le widget pour la sélection d'un compte bancaire
    """
    options = get_bank_account_options(kw["request"])
    widget = forms.get_select(options)
    return widget


def get_bank_account_validator(request):
    elements = (
        request.dbsession.execute(
            select(BankAccount.id).where(BankAccount.active.is_(True))
        )
        .scalars()
        .all()
    )
    return colander.OneOf(elements)


@colander.deferred
def deferred_bank_account_validator(node, kw):
    return get_bank_account_validator(kw["request"])


def get_customer_bank_options(request):
    """Collecte les banques clients"""
    return request.dbsession.execute(
        select(Bank.id, Bank.label).where(Bank.active.is_(True)).order_by(Bank.order)
    ).all()


def get_customer_bank_validator(request):
    elements = (
        request.dbsession.execute(select(Bank.id).where(Bank.active.is_(True)))
        .scalars()
        .all()
    )
    return colander.OneOf(elements)

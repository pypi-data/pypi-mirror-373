"""
    form schemas for invoices related views
"""
import datetime
from functools import partial

import colander
from colanderalchemy import SQLAlchemySchemaNode

from caerp import forms
from caerp.consts import AMOUNT_PRECISION
from caerp.forms.custom_types import AmountType, GlobalAllValidator
from caerp.forms.payments import (
    get_bank_account_validator,
    get_customer_bank_validator,
    get_payment_mode_default,
    get_payment_mode_validator,
)
from caerp.models.payments import BankAccount
from caerp.models.task.internalpayment import InternalPayment
from caerp.models.task.invoice import Invoice
from caerp.models.task.payment import Payment
from caerp.utils.strings import format_amount


def get_last_bank_remittance_id(request):
    from caerp.models.services.user import UserPrefsService

    result = UserPrefsService.get(request, "last_bank_remittance_id")
    if result is None:
        return ""
    else:
        return result


def get_amount_validator(request, invoice: Invoice):
    """
    Construit un validateur pour le montant de l'encaissement

    Le montant de l'encaissement doit être du même signe
    que le montant à payer

    Si le montant dépasse ce qui est attendu, il faut confirmer la saisie.
    """

    def check_amount_validator(node, values):
        topay = invoice.topay()
        if request.context is not invoice:
            topay += request.context.amount
        ttc = invoice.total()

        amount = values.get("amount", 0)
        confirm_amount = values.get("confirm_amount", False)

        if "amount" in node:
            amount_node = node["amount"]
        else:
            amount_node = node

        if ttc > 0 and amount < 0:
            raise colander.Invalid(
                amount_node,
                "Le montant de l'encaissement ne peut pas être négatif.",
            )
        elif ttc < 0 and amount > 0:
            raise colander.Invalid(
                amount_node,
                "Le montant de l'encaissement ne peut pas être positif.",
            )

        # On peut confirmer de l'encaissement si ce n'est pas une facture interne
        if not invoice.internal and confirm_amount:
            return True

        if topay > 0 and amount > topay:
            raise colander.Invalid(
                amount_node,
                "Le montant de l'encaissement {} est supérieur à {} "
                "(total TTC - somme des paiements). "
                "Veuillez confirmer votre saisie.".format(
                    format_amount(amount, precision=AMOUNT_PRECISION, grouping=False),
                    format_amount(topay, precision=AMOUNT_PRECISION, grouping=False),
                ),
            )

        elif topay < 0 and amount < topay:
            raise colander.Invalid(
                amount_node,
                "Le montant de l'encaissement est inférieur à {} "
                "(total TTC - somme des paiements). "
                "Veuillez confirmer votre saisie.".format(
                    format_amount(topay, precision=AMOUNT_PRECISION, grouping=False)
                ),
            )

    return check_amount_validator


def get_edit_bank_remittance_id_validator(request, invoice: Invoice):
    payment = request.context

    def check_bank_remittance_cohesion(node, values):
        """
        Si on édite, vérifie que le changement de mode et de banque
        se font uniquement en cas de nouvelle remise en banque
        """
        mode = values.get("mode", payment.mode)
        bank_id = values.get("bank_id", payment.bank_id)
        bank_remittance_id = values.get(
            "bank_remittance_id", payment.bank_remittance_id
        )

        print("Check bank remittance cohesion: ", mode, bank_id, bank_remittance_id)

        if payment.bank_remittance_id == bank_remittance_id:
            if mode != payment.mode:
                if "mode" in node:
                    node = node["mode"]
                raise colander.Invalid(
                    node,
                    (
                        "Le changement de mode de paiement ne peut se faire que "
                        "si vous créez une nouvelle remise en banque."
                    ),
                )
            if bank_id != payment.bank_id:
                if "bank_id" in node:
                    node = node["bank_id"]
                raise colander.Invalid(
                    node,
                    (
                        "Le changement de banque ne peut se faire que si vous créez "
                        "une nouvelle remise en banque."
                    ),
                )

    return check_bank_remittance_cohesion


def customize_fields(request, invoice, schema):
    customize = partial(forms.customize_field, schema)
    if "date" in schema:
        customize(
            "date",
            typ=colander.Date(),
            default=datetime.date.today(),
            missing=colander.required,
        )

    topay = invoice.topay()
    total = invoice.total()
    if total > 0 and topay < 0 or total < 0 and topay > 0:
        topay = 0

    customize("amount", default=topay, typ=AmountType(5), missing=colander.required)

    if "mode" in schema:
        customize(
            "mode",
            validator=get_payment_mode_validator(request),
            default=get_payment_mode_default(request),
            missing=colander.required,
        )

    if "customer_bank_id" in schema:
        customize(
            "customer_bank_id",
            validator=get_customer_bank_validator(request),
            missing=colander.drop,
        )

    if "issuer" in schema:
        customize("issuer", default=invoice.customer.label)

    if "bank_remittance_id" in schema:
        customize(
            "bank_remittance_id",
            default=get_last_bank_remittance_id(request),
            missing=colander.drop,
        )
        schema.add(
            colander.SchemaNode(
                colander.Boolean(),
                name="new_remittance_confirm",
                title="",
                label="Confirmer la création de cette remise en banque",
                missing=colander.drop,
            ),
        )

    if "check_number" in schema:
        customize("check_number", missing=colander.drop)

    if "bank_id" in schema:
        default_bank_id = forms.get_model_default_value(
            request, BankAccount, filters=BankAccount.active.is_(True)
        )
        customize(
            "bank_id",
            default=default_bank_id,
            validator=get_bank_account_validator(request),
            missing=colander.required,
        )
    return schema


def _get_payment_schema(request, invoice: Invoice, edit=False):
    """
    Schema de formulaire pour les Paiements de 'factures externes'
    """
    factory = Payment
    includes = (
        "date",
        "amount",
        "issuer",
        "customer_bank_id",
        "check_number",
    )
    validators = []

    if edit:
        # On n'édite pas de remise close
        payment = request.context
        if not payment.bank_remittance or not payment.bank_remittance.closed:
            includes += (
                "bank_remittance_id",
                "mode",
                "bank_id",
            )
            if payment.bank_remittance:
                validators.append(
                    get_edit_bank_remittance_id_validator(request, invoice)
                )
    else:
        includes += (
            "bank_remittance_id",
            "mode",
            "bank_id",
        )

    schema = SQLAlchemySchemaNode(
        factory,
        includes=includes,
    )
    validators.append(get_amount_validator(request, invoice))
    schema.validator = GlobalAllValidator(*validators)
    return schema


def _get_internalpayment_schema(request, invoice: Invoice, edit=False):
    factory = InternalPayment
    includes = (
        "date",
        "amount",
    )
    schema = SQLAlchemySchemaNode(
        factory,
        includes=includes,
    )
    schema.validator = get_amount_validator(request, invoice)
    customize_fields(request, invoice, schema)
    return schema


def get_cancel_payment_schema(request, invoice: Invoice):
    includes = ("date",)

    if invoice.internal:
        schema = SQLAlchemySchemaNode(InternalPayment, includes=includes)
    else:
        schema = SQLAlchemySchemaNode(Payment, includes=includes)
    customize_fields(request, invoice, schema)
    return schema


def get_payment_schema(request, invoice: Invoice, edit=False, cancelation=False):
    """
    Returns the schema for payment registration

    :param with_new_remittance_confirm: if True, a new remittance confirmation field is added
    :param gen_inverse_payment: if True, some fields are made read-only
    """
    if invoice.internal:
        schema = _get_internalpayment_schema(request, invoice, edit)
    else:
        schema = _get_payment_schema(request, invoice, edit)
        schema.add(
            colander.SchemaNode(
                colander.Boolean(),
                name="confirm_amount",
                title="Confirmer le dépassement de montant",
                missing=colander.drop,
            ),
        )

    customize_fields(request, invoice, schema)
    schema.add(forms.come_from_node(name="come_from"))
    schema.add(
        colander.SchemaNode(
            colander.Boolean(),
            name="resulted",
            title="Soldée",
            description="Indique que la facture est soldée (ne recevra plus "
            "de paiement), si le montant indiqué correspond au montant "
            "de la facture celle-ci est soldée automatiquement",
            default=False,
            missing=colander.drop,
        )
    )

    return schema

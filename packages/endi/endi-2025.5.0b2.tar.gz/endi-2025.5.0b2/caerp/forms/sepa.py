import datetime

import colander
import colanderalchemy
from sqlalchemy import select

from caerp.forms import customize_field
from caerp.forms.company import company_node
from caerp.forms.custom_types import CustomSet
from caerp.forms.lists import FilterSchema
from caerp.forms.user import antenne_node, user_node
from caerp.models.payments import BankAccount
from caerp.models.sepa import BaseSepaWaitingPayment, SepaCreditTransfer
from caerp.services.bank_account import (
    get_active_bank_accounts_ids,
    get_default_bank_account_id,
)
from caerp.services.sepa import get_available_sepa_pain_versions
from caerp.utils.sepa.credit_transfer import SepaCreditTransferXmlFactory


def get_waiting_payment_filter_schema(request):
    """
    Build the form schema used to validate
    the SepaWaitingPayment query filters
    """

    class SepaWaitingFilterSchema(FilterSchema):
        doctype = colander.SchemaNode(
            colander.String(),
            title="Type de document",
            missing="all",
            validator=colander.OneOf(
                [
                    "all",
                    "supplier_invoice",
                    "expense",
                ]
            ),
        )
        sepa_credit_transfer_id = colander.SchemaNode(
            colander.Integer(),
            title="Antenne",
            missing=None,
        )
        paid_status = colander.SchemaNode(
            colander.String(),
            title="Statut de paiement",
            missing="all",
            validator=colander.OneOf(["all", "wait", "paid"]),
        )
        official_number = colander.SchemaNode(
            colander.String(),
            title="Numéro du document",
            missing="",
        )
        with_iban = colander.SchemaNode(
            colander.Boolean(),
            title="Avec IBAN",
            missing=False,
        )
        user_ids = user_node(multiple=True, missing=None, no_widget=True)
        company_ids = company_node(multiple=True, missing=None, no_widget=True)
        antenne_ids = antenne_node(multiple=True, missing=None, no_widget=True)

    return SepaWaitingFilterSchema()


def get_set_payments_schema(request):
    """
    Schema validating the association of a BaseSepaWaitingPayment with
    a SepaCreditTransfer
    """
    available_waiting_payment_ids = (
        request.dbsession.execute(
            select(BaseSepaWaitingPayment.id).where(
                BaseSepaWaitingPayment.paid_status == BaseSepaWaitingPayment.WAIT_STATUS
            )
        )
        .scalars()
        .all()
    )

    payment_schema = colander.SchemaNode(
        colander.Mapping(),
        colander.SchemaNode(
            colander.Integer(),
            validator=colander.OneOf(available_waiting_payment_ids),
            name="id",
        ),
    )
    schema = colander.SchemaNode(colander.Mapping())
    schema.add(colander.SequenceSchema(payment_schema, name="payments"))

    return schema


def get_sepa_credit_transfer_metadata_form_schema(request):
    """
    Build a schema to configure the metadata form for a SEPA Credit Transfer.

    .. note: Metadata are set before generating the XML File
    """
    schema = colanderalchemy.SQLAlchemySchemaNode(
        SepaCreditTransfer,
        includes=(
            "bank_account_id",
            "execution_date",
            "sepa_pain_version",
        ),
    )
    date_error_message = (
        "Veuillez fournir une date entre aujourd'hui et dans les 30 prochaines jours."
    )
    customize_field(
        schema,
        "execution_date",
        default=datetime.date.today(),
        validator=colander.Range(
            datetime.date.today(),
            datetime.date.today() + datetime.timedelta(days=30),
            min_err=date_error_message,
            max_err=date_error_message,
        ),
    )
    customize_field(
        schema,
        "bank_account_id",
        validator=colander.OneOf(
            get_active_bank_accounts_ids(
                request,
                more_filters=[
                    BankAccount.iban.is_not(None),
                    BankAccount.bic.is_not(None),
                ],
            )
        ),
        default=get_default_bank_account_id(
            request,
            more_filters=[
                BankAccount.iban.is_not(None),
                BankAccount.bic.is_not(None),
            ],
        ),
        missing=colander.required,
    )

    customize_field(
        schema,
        "sepa_pain_version",
        default=SepaCreditTransferXmlFactory.DEFAULT_VERSION,
        validator=colander.OneOf(get_available_sepa_pain_versions()),
    )
    return schema


def get_sepa_credit_transfer_filter_schema(request):
    class SepaCreditTransferFilterSchema(FilterSchema):
        bank_account_id = colander.SchemaNode(
            colander.Integer(),
            title="Compte bancaire",
            missing=None,
        )
        execution_date_start = colander.SchemaNode(
            colander.Date(),
            title="Date de début",
            missing=None,
        )
        execution_date_end = colander.SchemaNode(
            colander.Date(),
            title="Date de fin",
            missing=None,
        )
        status = colander.SchemaNode(
            CustomSet(),
            title="Status",
            default=("closed", "cancelled"),
            missing=("closed", "cancelled"),
        )

    return SepaCreditTransferFilterSchema()

import logging
from typing import Optional

from pyramid.csrf import get_csrf_token
from sqlalchemy import func, or_, select
from sqlalchemy.orm import aliased, with_polymorphic

from caerp.consts.permissions import PERMISSIONS
from caerp.controllers.sepa.credit_transfer_order import (
    add_waiting_payment_to_sepa_credit_transfer,
    generate_sepa_credit_transfer_xml_file,
    remove_waiting_payment_from_sepa_credit_transfer,
)
from caerp.exception import MissingConfigError
from caerp.forms import merge_session_with_post
from caerp.forms.jsonschema import convert_to_jsonschema
from caerp.forms.sepa import (
    get_sepa_credit_transfer_filter_schema,
    get_sepa_credit_transfer_metadata_form_schema,
    get_set_payments_schema,
    get_waiting_payment_filter_schema,
)
from caerp.models.company import Company
from caerp.models.expense.sheet import ExpenseSheet
from caerp.models.payments import BankAccount
from caerp.models.sepa import (
    BaseSepaWaitingPayment,
    ExpenseSepaWaitingPayment,
    SepaCreditTransfer,
    SupplierInvoiceSupplierSepaWaitingPayment,
)
from caerp.models.supply.supplier_invoice import SupplierInvoice
from caerp.models.third_party.supplier import Supplier
from caerp.models.user.login import Login
from caerp.models.user.user import User
from caerp.models.user.userdatas import AntenneOption
from caerp.services.bank_account import get_active_bank_accounts_for_select
from caerp.services.sepa import get_available_sepa_pain_versions
from caerp.services.serializers import serializers
from caerp.services.serializers.base import BaseSerializer
from caerp.utils.rest.apiv1 import RestError
from caerp.utils.rest.parameters import FieldOptions, LoadOptions
from caerp.views import BaseRestViewV2
from caerp.views.sepa.routes import (
    API_SEPA_COLLECTION_ROUTE,
    API_SEPA_ITEM_ROUTE,
    API_SEPA_WAITING_PAYMENT_ITEM_ROUTE,
    API_SEPA_WAITING_PAYMENTS_COLLECTION_ROUTE,
)

logger = logging.getLogger(__name__)

supplier_company_alias = aliased(Company)
supplier_supplier_alias = aliased(Supplier)
supplier_payer_alias = aliased(User)
expense_user_alias = aliased(User)
expense_sheet_company_alias = aliased(Company)
all_waiting_payments = with_polymorphic(
    BaseSepaWaitingPayment,
    [ExpenseSepaWaitingPayment, SupplierInvoiceSupplierSepaWaitingPayment],
)


# Champs par défaut renvoyés lorsque l'on requête un/des BaseSepaWaitingPayment
DEFAULT_WAITING_PAYMENTS_FIELDS = FieldOptions.from_dict(
    {
        "attributes": [
            "id",
            "order_id",
            "amount",
            "amount_label",
            "paid_status",
            "payment_id",
            "type_",
        ],
        "relationships": {
            "expense_sheet": {
                "attributes": ["id", "title", "label", "official_number", "date"],
                "relationships": {
                    "user": {
                        "attributes": ["id", "label", "has_bank_account"],
                        "relationships": {},
                    },
                    "company": {"attributes": ["name", "id"], "relationships": {}},
                },
            },
            "supplier_invoice": {
                "attributes": ["id", "name", "label", "official_number", "date"],
                "relationships": {
                    "supplier": {
                        "attributes": ["id", "label", "has_bank_account"],
                        "relationships": {},
                    },
                    "payer": {
                        "attributes": ["id", "label", "has_bank_account"],
                        "relationships": {},
                    },
                    "company": {"attributes": ["name", "id"], "relationships": {}},
                },
            },
        },
    }
)


class SepaWaitingPaymentRestView(BaseRestViewV2):
    """
    GET ?fields=id,amount,expense_sheet[id,official_number,total,month,year,user[id,label,has_bank_account]]&filter_doctype=expense_sheet&filter_antenne_id=15&sort.sort=date&sort.sortDirection=desc&pagination.page=1&pagination.per_page=10

    En entrée :

    - la query qui est convertie en LoadOptions

    En retour

    - le RestCollectionResponse qui est converti en json
    """

    serializer_class = serializers["sepa_waiting_payment"]
    sort_columns = {
        "amount": BaseSepaWaitingPayment.amount,
        "status": BaseSepaWaitingPayment.paid_status,
        "official_number": func.coalesce(
            ExpenseSheet.official_number, SupplierInvoice.official_number
        ),
        "supplier_name": supplier_supplier_alias.name,
        "user": func.coalesce(
            expense_user_alias.lastname, supplier_payer_alias.lastname
        ),
        "company": func.coalesce(
            supplier_company_alias.name, expense_sheet_company_alias.name
        ),
        "doctype": BaseSepaWaitingPayment.type_,
    }
    default_sort = "amount"

    def get_filter_schema(self, load_options: LoadOptions):
        return get_waiting_payment_filter_schema(self.request)

    def filter_doctype(self, query, filters):
        type_ = filters.get("doctype")
        if type_ in ("supplier_invoice", "expense"):
            logger.debug("  + Filtering by doctype : {type_}")
            query = query.where(
                BaseSepaWaitingPayment.type_ == f"{type_}_sepa_waiting_payment"
            )
        return query

    def filter_paid_status(self, query, filters):
        paid_status = filters.get("paid_status")
        if paid_status in ("wait", "paid"):
            query = query.where(BaseSepaWaitingPayment.paid_status == paid_status)
        return query

    def filter_official_number(self, query, filters):
        official_number = filters.get("official_number")
        if official_number:
            logger.debug("  + Filtering by official_number : {official_number}")
            query = query.where(
                or_(
                    ExpenseSheet.official_number.like(f"%{official_number}%"),
                    SupplierInvoice.official_number.like(f"%{official_number}%"),
                )
            )
        return query

    def filter_sepa_credit_transfer_id(self, query, filters):
        sepa_credit_transfer_id = filters.get("sepa_credit_transfer_id")
        if sepa_credit_transfer_id:
            query = query.where(
                BaseSepaWaitingPayment.sepa_credit_transfer_id
                == sepa_credit_transfer_id
            )
        return query

    def filter_with_iban(self, query, filters):
        with_iban = filters.get("with_iban")
        if with_iban:
            query = query.where(
                or_(
                    expense_user_alias.bank_account_iban.is_not(None),
                    supplier_supplier_alias.bank_account_iban.is_not(None),
                    supplier_payer_alias.bank_account_iban.is_not(None),
                )
            )
        return query

    def filter_antenne_ids(self, query, filters):
        antenne_ids = filters.get("antenne_ids")
        if antenne_ids:
            logger.debug("  + Filtering by antenne_ids : {antenne_ids}")

            query = query.where(
                or_(
                    supplier_company_alias.antenne_id.in_(antenne_ids),
                    expense_sheet_company_alias.antenne_id.in_(antenne_ids),
                )
            )
        return query

    def filter_user_ids(self, query, filters):
        values = filters.get("user_ids")
        if values:
            query = query.where(
                or_(
                    expense_user_alias.id.in_(values),
                    supplier_payer_alias.id.in_(values),
                )
            )
        return query

    def filter_supplier_ids(self, query, filters):
        values = filters.get("supplier_ids")
        if values:
            query = query.where(supplier_supplier_alias.id.in_(values))
        return query

    def filter_company_ids(self, query, filters):
        values = filters.get("company_ids")
        if values:
            query = query.where(
                or_(
                    supplier_company_alias.id.in_(values),
                    expense_sheet_company_alias.id.in_(values),
                )
            )
        return query

    def build_collection_query(
        self, filters: Optional[dict], fields: Optional[FieldOptions]
    ):
        query = (
            select(
                all_waiting_payments,
                func.count(BaseSepaWaitingPayment.id).over().label("total"),
            )
            .outerjoin(all_waiting_payments.ExpenseSepaWaitingPayment.expense_sheet)
            .outerjoin(
                expense_user_alias, expense_user_alias.id == ExpenseSheet.user_id
            )
            .outerjoin(
                expense_sheet_company_alias,
                expense_sheet_company_alias.id == ExpenseSheet.company_id,
            )
            .outerjoin(
                all_waiting_payments.SupplierInvoiceSupplierSepaWaitingPayment.supplier_invoice
            )
            .outerjoin(
                supplier_supplier_alias,
                supplier_supplier_alias.id == SupplierInvoice.supplier_id,
            )
            .outerjoin(
                supplier_payer_alias,
                supplier_payer_alias.id == SupplierInvoice.payer_id,
            )
            .outerjoin(
                supplier_company_alias,
                supplier_company_alias.id == SupplierInvoice.company_id,
            )
        )
        query = self._filter(query, filters)
        return query

    def _get_serializer(self, fields) -> BaseSerializer:
        return self.serializer_class(fields=fields, serializer_registry=serializers)

    def get(self) -> dict:
        load_options = LoadOptions.from_request(self.request)
        fields = self.validate_fields(load_options)
        serializer = self._get_serializer(fields)
        return serializer.run(self.request, self.context)


# Champs par défaut renvoyés lorsque l'on effectue une requête GET
# sur un SepaCreditTransfer
DEFAULT_CREDIT_TRANSFER_FIELDS = FieldOptions.from_dict(
    {
        "attributes": [
            "id",
            "reference",
            "bank_id",
            "status",
            "file_id",
            "execution_date",
            "user_id",
            "amount_label",
        ],
        "relationships": {
            "sepa_waiting_payments": DEFAULT_WAITING_PAYMENTS_FIELDS,
            "bank_account": {"attributes": ["id", "label"]},
            "user": {"attributes": ["id", "label"]},
        },
    }
)


class SepaCreditTransferRestView(BaseRestViewV2):
    sort_columns = {
        "amount": "amount",
        "execution_date": "execution_date",
        "user": User.lastname,
    }
    default_sort = "execution_date"
    default_sort_direction = "desc"

    def get_schema(self, submitted: dict):
        if "payments" in submitted:
            logger.debug("  + Using set payments schema")
            return get_set_payments_schema(self.request)
        elif "bank_account_id" in submitted or "execution_date" in submitted:
            logger.debug("  + Using metadata schema")
            return get_sepa_credit_transfer_metadata_form_schema(self.request)
        return super().get_schema(submitted)

    def _edit_element(self, schema, attributes):
        if "payments" in attributes:
            payment_ids = [p["id"] for p in attributes["payments"]]
            payments = (
                self.dbsession.execute(
                    select(BaseSepaWaitingPayment).where(
                        BaseSepaWaitingPayment.id.in_(payment_ids)
                    )
                )
                .scalars()
                .all()
            )
            removed_payments = [
                p for p in self.context.sepa_waiting_payments if p not in payments
            ]
            for payment in removed_payments:
                remove_waiting_payment_from_sepa_credit_transfer(
                    self.request, self.context, payment
                )
            for payment in payments:
                add_waiting_payment_to_sepa_credit_transfer(
                    self.request, self.context, payment
                )
        elif (
            "bank_account_id" in attributes
            or "execution_date" in attributes
            or "sepa_pain_version" in attributes
        ):
            merge_session_with_post(self.context, attributes)
            self.dbsession.flush()
            try:
                generate_sepa_credit_transfer_xml_file(self.request, self.context)
            except AssertionError as e:
                raise RestError(str(e))
            except MissingConfigError as e:
                raise RestError(getattr(e, "message", "Erreur inconnue"))

            return self.context

        return self.context

    def format_item_result(self, model):
        logger.debug(f"  + Serializing item : {model}")
        serializer = serializers["sepa_credit_transfer"]
        result = serializer(
            fields=DEFAULT_CREDIT_TRANSFER_FIELDS, serializer_registry=serializers
        ).run(self.request, model)
        logger.debug(f"  + Formatted item : {result}")
        return result

    def form_config(self):
        return {
            "schemas": {
                # "filter": convert_to_jsonschema(get_filter_schema(self.request)),
                "default": convert_to_jsonschema(
                    get_sepa_credit_transfer_metadata_form_schema(self.request)
                )
            },
            "options": {
                "antennes": [
                    {"id": antenne[0], "label": antenne[1]}
                    for antenne in self.dbsession.execute(
                        select(AntenneOption.id, AntenneOption.label)
                    ).all()
                ],
                "users": [
                    {"id": user.id, "label": user.label}
                    for user in self.dbsession.execute(
                        select(User)
                        .join(User.login)
                        .where(Login.active == True)
                        .where(User.special == 0)
                    )
                    .scalars()
                    .all()
                ],
                "companies": [
                    {"id": a[0], "label": a[1]}
                    for a in self.dbsession.execute(
                        select(Company.id, Company.name).where(Company.active == True)
                    ).all()
                ],
                "bank_accounts": [
                    {"id": b[0], "label": b[1]}
                    for b in get_active_bank_accounts_for_select(
                        self.request,
                        more_filters=[
                            BankAccount.iban.is_not(None),
                            BankAccount.bic.is_not(None),
                        ],
                    )
                ],
                "sepa_pain_versions": [
                    {"id": version, "label": version}
                    for version in get_available_sepa_pain_versions()
                ],
                "csrf_token": get_csrf_token(self.request),
            },
        }

    def get_filter_schema(self, load_options: LoadOptions):
        return get_sepa_credit_transfer_filter_schema(self.request)

    def filter_doctype(self, query, filters):
        type_ = filters.get("doctype")
        if type_ in ("supplier_invoice", "expense"):
            logger.debug("  + Filtering by doctype : {type_}")
            query = query.where(
                BaseSepaWaitingPayment.type_ == f"{type_}_sepa_waiting_payment"
            )
        return query

    def filter_paid_status(self, query, filters):
        paid_status = filters.get("paid_status")
        if paid_status in ("wait", "paid"):
            query = query.where(BaseSepaWaitingPayment.paid_status == paid_status)
        return query

    def filter_official_number(self, query, filters):
        official_number = filters.get("official_number")
        if official_number:
            logger.debug("  + Filtering by official_number : {official_number}")
            query = query.where(
                or_(
                    ExpenseSheet.official_number.like(f"%{official_number}%"),
                    SupplierInvoice.official_number.like(f"%{official_number}%"),
                )
            )
        return query

    def filter_status(self, query, filters):
        status = filters.get("status")
        if status:
            query = query.where(SepaCreditTransfer.status.in_(status))
        return query

    def sort_by_amount(self, query, sort, sort_func):
        subq = (
            select([func.sum(BaseSepaWaitingPayment.amount).label("total")])
            .where(
                BaseSepaWaitingPayment.sepa_credit_transfer_id == SepaCreditTransfer.id
            )
            .scalar_subquery()
        )
        return query.order_by(sort_func(subq))

    def build_collection_query(
        self, filters: Optional[dict], fields: Optional[FieldOptions]
    ):
        query = (
            select(
                SepaCreditTransfer,
                func.count(SepaCreditTransfer.id).over().label("total"),
            )
            .join(User, User.id == SepaCreditTransfer.user_id)
            .join(BankAccount, BankAccount.id == SepaCreditTransfer.bank_account_id)
        )
        query = self._filter(query, filters)
        return query

    def validate_fields(self, load_options: LoadOptions) -> Optional[FieldOptions]:
        return load_options.fields or DEFAULT_CREDIT_TRANSFER_FIELDS

    def _get_serializer(self, fields):
        serializer = serializers["sepa_credit_transfer"]
        result = serializer(fields=fields, serializer_registry=serializers)
        return result


def includeme(config):
    config.add_rest_service(
        factory=SepaWaitingPaymentRestView,
        route_name=API_SEPA_WAITING_PAYMENT_ITEM_ROUTE,
        collection_route_name=API_SEPA_WAITING_PAYMENTS_COLLECTION_ROUTE,
        collection_view_rights=PERMISSIONS["global.manage_accounting"],
        view_rights=PERMISSIONS["global.manage_accounting"],
    )
    config.add_rest_service(
        SepaCreditTransferRestView,
        collection_route_name=API_SEPA_COLLECTION_ROUTE,
        collection_view_rights=PERMISSIONS["global.manage_accounting"],
        route_name=API_SEPA_ITEM_ROUTE,
        context=SepaCreditTransfer,
        view_rights=PERMISSIONS["global.manage_accounting"],
        edit_rights=PERMISSIONS["context.edit"],
    )
    config.add_view(
        SepaCreditTransferRestView,
        attr="form_config",
        route_name=API_SEPA_ITEM_ROUTE,
        context=SepaCreditTransfer,
        renderer="json",
        request_method="GET",
        request_param="form_config",
        permission=PERMISSIONS["global.manage_accounting"],
    )

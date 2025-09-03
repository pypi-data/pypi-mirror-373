"""
Views related to payments edition
"""
import logging
from caerp.consts.permissions import PERMISSIONS
from pyramid.httpexceptions import HTTPFound

from caerp.controllers.state_managers import check_node_resulted

from caerp.controllers.supplier_invoice.payment import (
    cancel_sepa_waiting_payment,
    delete_supplier_invoice_payment,
    record_supplier_invoice_payment_for_user,
    record_supplier_invoice_payment_for_supplier,
)
from caerp.models.supply import (
    SupplierInvoiceSupplierPayment,
    BaseSupplierInvoicePayment,
    SupplierInvoice,
)
from caerp.utils.widgets import Link

from caerp.forms import merge_session_with_post
from caerp.forms.supply.supplier_invoice import (
    UserPaymentSchema,
    SupplierPaymentSchema,
)

from caerp.views import (
    BaseView,
    TreeMixin,
    BaseFormView,
)
from caerp.views.supply.utils import get_supplier_doc_url
from caerp.views.supply.invoices.views import SupplierInvoiceEditView
from caerp.views.supply.invoices.routes import ITEM_ROUTE as SUPPLIER_INVOICE_ROUTE

from .base import (
    BasePaymentEditView,
    BasePaymentDeleteView,
    get_delete_confirm_message,
    get_warning_message,
)

logger = logging.getLogger(__name__)


class SupplierInvoicePaymentView(BaseView, TreeMixin):
    route_name = "supplier_payment"

    @property
    def tree_url(self):
        return self.request.route_path(
            self.route_name,
            id=self.context.id,
        )

    @property
    def title(self):
        return "Paiement pour la facture fournisseur {0}".format(
            self.context.parent.official_number
        )

    def stream_actions(self):
        parent_url = self.request.route_path(
            SUPPLIER_INVOICE_ROUTE,
            id=self.context.parent.id,
        )
        if self.request.has_permission(PERMISSIONS["context.edit_payment"]):
            _query = dict(action="edit")
            if self.request.is_popup:
                _query["popup"] = "1"
            edit_url = self.request.route_path(
                self.route_name, id=self.context.id, _query=_query
            )

            yield Link(
                edit_url,
                label="Modifier",
                title="Modifier les informations du paiement",
                icon="pen",
                css="btn btn-primary",
            )
        if self.request.has_permission(PERMISSIONS["context.delete_payment"]):
            del_url = self.request.route_path(
                self.route_name,
                id=self.context.id,
                _query=dict(action="delete", come_from=parent_url),
            )
            confirm = get_delete_confirm_message(self.context, "décaissement", "ce")
            yield Link(
                del_url,
                label="Supprimer",
                title="Supprimer le paiement",
                icon="trash-alt",
                confirm=confirm,
                css="negative",
            )

    def get_export_button(self):
        if self.request.has_permission(PERMISSIONS["global.manage_accounting"]):
            if self.context.exported:
                label = "Forcer l'export des écritures de ce paiement"
            else:
                label = "Exporter les écritures de ce paiement"
            return Link(
                self.request.route_path(
                    "/export/treasury/supplier_payments/{id}",
                    id=self.context.id,
                    _query=dict(come_from=self.tree_url, force=True),
                ),
                label=label,
                title=label,
                icon="file-export",
                css="btn btn-primary",
            )

    def __call__(self):
        self.populate_navigation()
        return dict(
            title=self.title,
            actions=self.stream_actions(),
            export_button=self.get_export_button(),
            document_number=f"Facture fournisseur {self.context.parent.official_number}",
            money_flow_type="Ce décaissement",
        )


class BaseSupplierInvoicePaymentView(BaseFormView, TreeMixin):
    # Must be defined by subclasses
    payment_factory = None
    success_msg = ""

    def before(self, form):
        self.populate_navigation()

    def redirect(self, come_from):
        if come_from:
            return HTTPFound(come_from)
        else:
            return HTTPFound(get_supplier_doc_url(self.request))

    def submit_success(self, appstruct):
        """
        Create the payment
        """
        logger.debug(
            f"+ Submitting a new payment with factory {self.payment_factory.__name__}"
        )
        logger.debug(appstruct)
        come_from = appstruct.pop("come_from", None)
        if self.payment_factory is not None:
            self.payment_factory(self.request, self.context, **appstruct)
        else:
            raise NotImplementedError("No payment factory defined")
        self.request.session.flash(self.success_msg)
        # FIXME
        # notify_status_changed(self.request, self.context.paid_status)
        return self.redirect(come_from)


class SupplierPaymentAddView(BaseSupplierInvoicePaymentView):
    """
    Called for setting a payment to an user on a SupplierInvoice
    """

    route_name = f"{SUPPLIER_INVOICE_ROUTE}/add_supplier_payment"
    schema = SupplierPaymentSchema()
    title = "Saisie d'un paiement fournisseur"
    success_msg = "Le paiement a bien été enregistré"
    payment_factory = staticmethod(record_supplier_invoice_payment_for_supplier)


class UserPaymentAddView(BaseSupplierInvoicePaymentView):
    """
    Called for setting a payment to a supplier on a SupplierInvoice
    """

    route_name = f"{SUPPLIER_INVOICE_ROUTE}/add_user_payment"
    schema = UserPaymentSchema()
    title = "Saisie d'un remboursement entrepreneur"
    success_msg = "Le remboursement a bien été enregistré"
    payment_factory = staticmethod(record_supplier_invoice_payment_for_user)


class SupplierPaymentEdit(BasePaymentEditView):
    route_name = "supplier_payment"

    def get_schema(self):
        payment = self.context
        if isinstance(payment, SupplierInvoiceSupplierPayment):
            schema = SupplierPaymentSchema()
        else:
            schema = UserPaymentSchema()
        return schema

    @property
    def warn_message(self):
        return get_warning_message(self.context, "décaissement", "ce")

    def get_default_redirect(self):
        return self.request.route_path("supplier_payment", id=self.context.id)

    def edit_payment(self, appstruct):
        invoice = self.context.supplier_invoice
        payment_obj = self.context
        # update the payment
        merge_session_with_post(payment_obj, appstruct)
        self.dbsession.merge(payment_obj)
        check_node_resulted(self.request, invoice)
        self.dbsession.merge(invoice)
        return payment_obj


class SupplierPaymentDeleteView(BasePaymentDeleteView):
    def delete_payment(self):
        supplier_invoice = self.context.supplier_invoice
        if self.context.sepa_waiting_payment:
            cancel_sepa_waiting_payment(self.request, self.context.sepa_waiting_payment)
        else:
            delete_supplier_invoice_payment(
                self.request, supplier_invoice, self.context
            )
        return supplier_invoice

    def parent_url(self, parent_id):
        return self.request.route_path(SUPPLIER_INVOICE_ROUTE, id=parent_id)


def includeme(config):
    config.add_tree_view(
        SupplierInvoicePaymentView,
        parent=SupplierInvoiceEditView,
        permission=PERMISSIONS["company.view"],
        renderer="/payment.mako",
        context=BaseSupplierInvoicePayment,
    )
    config.add_tree_view(
        SupplierPaymentAddView,
        parent=SupplierInvoiceEditView,
        permission=PERMISSIONS["context.add_payment_supplier_invoice"],
        renderer="base/formpage.mako",
        context=SupplierInvoice,
    )
    config.add_tree_view(
        UserPaymentAddView,
        parent=SupplierInvoiceEditView,
        permission=PERMISSIONS["context.add_payment_supplier_invoice"],
        renderer="base/formpage.mako",
        context=SupplierInvoice,
    )
    config.add_tree_view(
        SupplierPaymentEdit,
        parent=SupplierInvoicePaymentView,
        permission=PERMISSIONS["context.edit_payment"],
        request_param="action=edit",
        renderer="/base/formpage.mako",
        context=BaseSupplierInvoicePayment,
    )
    config.add_view(
        SupplierPaymentDeleteView,
        route_name="supplier_payment",
        permission=PERMISSIONS["context.delete_payment"],
        request_param="action=delete",
        context=BaseSupplierInvoicePayment,
    )

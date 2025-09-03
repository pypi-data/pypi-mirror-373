import logging
from caerp.consts.permissions import PERMISSIONS
from pyramid.httpexceptions import HTTPFound
from caerp.controllers.expense.payment import (
    cancel_sepa_waiting_payment,
    delete_expense_payment,
    record_expense_payment,
)

from caerp.models.expense.payment import ExpensePayment

from caerp.models.expense.sheet import ExpenseSheet
from caerp.utils.widgets import Link

from caerp.forms import merge_session_with_post
from caerp.forms.expense import ExpensePaymentSchema

from caerp.views import BaseView, TreeMixin, BaseFormView, submit_btn, cancel_btn
from caerp.views.expenses.expense import ExpenseSheetEditView

from .base import (
    BasePaymentEditView,
    BasePaymentDeleteView,
    get_delete_confirm_message,
    get_warning_message,
)

logger = logging.getLogger(__name__)


class ExpensePaymentView(BaseView, TreeMixin):
    """
    Simple expense payment view
    """

    route_name = "expense_payment"

    @property
    def tree_url(self):
        return self.request.route_path(
            self.route_name,
            id=self.context.id,
        )

    def stream_actions(self):
        parent_url = self.request.route_path(
            "/expenses/{id}",
            id=self.context.parent.id,
        )
        if self.request.has_permission(PERMISSIONS["context.edit_payment"]):
            _query = dict(action="edit")
            if self.request.is_popup:
                _query["popup"] = "1"
            edit_url = self.request.route_path(
                "expense_payment", id=self.context.id, _query=_query
            )

            yield Link(
                edit_url,
                label="Modifier",
                title="Modifier les informations du paiement",
                icon="pen",
                css="btn btn-primary",
            )
        if self.request.has_permission(PERMISSIONS["context.delete_payment"]):
            _query = dict(action="delete", come_from=parent_url)
            if self.request.is_popup:
                _query["popup"] = 1
            del_url = self.request.route_path(
                "expense_payment", id=self.context.id, _query=_query
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
                    "/export/treasury/expense_payments/{id}",
                    id=self.context.id,
                    _query=dict(come_from=self.tree_url, force=True),
                ),
                label=label,
                title=label,
                icon="file-export",
                css="btn btn-primary",
            )

    @property
    def title(self):
        return "Paiement pour la note de dépenses {0}".format(self.context.parent.id)

    def __call__(self):
        self.populate_navigation()
        return dict(
            title=self.title,
            actions=self.stream_actions(),
            export_button=self.get_export_button(),
            money_flow_type="Ce décaissement",
            document_number=f"Note de dépense {self.context.parent.official_number}",
        )


class ExpensePaymentAddView(BaseFormView, TreeMixin):
    """
    Called for setting a payment on an expensesheet
    """

    schema = ExpensePaymentSchema()
    title = "Saisie d'un paiement"
    buttons = (submit_btn, cancel_btn)

    def before(self, form):
        self.populate_navigation()
        return super().before(form)

    def redirect(self, come_from):
        if come_from:
            return HTTPFound(come_from)
        else:
            return HTTPFound(
                self.request.route_path("/expenses/{id}", id=self.request.context.id)
            )

    def submit_success(self, appstruct):
        """
        Create the payment
        """
        logger.debug("+ Submitting an expense payment")
        logger.debug(appstruct)
        come_from = appstruct.pop("come_from", None)

        record_expense_payment(self.request, self.context, **appstruct)
        self.request.session.flash("Le paiement a bien été enregistré")
        return self.redirect(come_from)

    def cancel_success(self, appstruct):
        return self.redirect(appstruct.get("come_from", None))

    cancel_failure = cancel_success


class ExpensePaymentEdit(BasePaymentEditView):
    route_name = "expense_payment"

    def get_schema(self):
        return ExpensePaymentSchema()

    @property
    def warn_message(self):
        return get_warning_message(self.context, "décaissement", "ce")

    def get_default_redirect(self):
        """
        Get the default redirection path
        """
        return self.request.route_path("expense_payment", id=self.context.id)

    def edit_payment(self, appstruct):
        payment_obj = self.context
        # update the payment
        merge_session_with_post(payment_obj, appstruct)
        self.dbsession.merge(payment_obj)
        return payment_obj


class ExpensePaymentDeleteView(BasePaymentDeleteView):
    def delete_payment(self):
        expense_sheet = self.context.expense
        if self.context.sepa_waiting_payment:
            logger.debug("First Cancelling SEPA waiting payment")
            cancel_sepa_waiting_payment(self.request, self.context.sepa_waiting_payment)
        else:
            logger.debug("Delete the payment directly")
            delete_expense_payment(self.request, expense_sheet, self.context)
        return expense_sheet

    def parent_url(self, parent_id):
        return self.request.route_path("expensesheet", id=parent_id)


def includeme(config):
    config.add_tree_view(
        ExpensePaymentView,
        parent=ExpenseSheetEditView,
        permission=PERMISSIONS["company.view"],
        renderer="/payment.mako",
        context=ExpensePayment,
    )
    config.add_tree_view(
        ExpensePaymentAddView,
        parent=ExpenseSheetEditView,
        route_name="/expenses/{id}/addpayment",
        permission=PERMISSIONS["context.add_payment_expensesheet"],
        renderer="base/formpage.mako",
        context=ExpenseSheet,
    )
    config.add_tree_view(
        ExpensePaymentEdit,
        parent=ExpensePaymentView,
        permission=PERMISSIONS["context.edit_payment"],
        request_param="action=edit",
        renderer="/base/formpage.mako",
        context=ExpensePayment,
    )
    config.add_view(
        ExpensePaymentDeleteView,
        route_name="expense_payment",
        permission=PERMISSIONS["context.delete_payment"],
        request_param="action=delete",
        context=ExpensePayment,
    )

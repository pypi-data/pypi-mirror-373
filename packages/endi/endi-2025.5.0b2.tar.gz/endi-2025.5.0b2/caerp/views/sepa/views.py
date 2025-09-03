"""
Vue globale pour l'accès au ordre de virement SEPA

1- Liste des ordres de virement SEPA
2- Création d'un ordre de virement SEPA
3- Édition d'un ordre de virement SEPA
"""
from pyramid.httpexceptions import HTTPFound

from caerp.consts.permissions import PERMISSIONS
from caerp.controllers.expense.payment import (
    delete_sepa_waiting_payment as delete_sepa_waiting_payment_expense_sheet,
)
from caerp.controllers.sepa.credit_transfer_order import (
    cancel_sepa_credit_transfer,
    create_sepa_credit_transfer,
)
from caerp.controllers.supplier_invoice.payment import (
    delete_supplier_invoice_sepa_waiting_payment,
)
from caerp.models.sepa import (
    BaseSepaWaitingPayment,
    ExpenseSepaWaitingPayment,
    SepaCreditTransfer,
)
from caerp.resources import sepa_credit_transfer_js
from caerp.services.sepa import get_open_sepa_credit_transfer, has_waiting_payments
from caerp.views import DeleteView

from .routes import (
    API_SEPA_ITEM_ROUTE,
    SEPA_CREDIT_TRANSFER_CANCEL_ROUTE,
    SEPA_CREDIT_TRANSFER_COLLECTION_ROUTE,
    SEPA_WAITING_PAYMENT_ITEM_ROUTE,
)


def sepa_credit_transfer_entry_point_view(request):
    """
    Point d'entrée pour l'accès aux ordre de virement SEPA

    Si on a un ordre de virement SEPA en cours de modification, on redirige sur la page d'édition
    Sinon, on redirige sur la page de création
    :param request: la requête Pyramid
    """
    sepa_credit_transfer_js.need()
    credit_transfer = get_open_sepa_credit_transfer(request)
    if not credit_transfer:
        credit_transfer = create_sepa_credit_transfer(request)
    return {
        "title": "Ordre de virement SEPA",
        "js_app_options": {
            "credit_transfer_id": credit_transfer.id,
            "form_config_url": request.route_path(
                API_SEPA_ITEM_ROUTE,
                id=credit_transfer.id,
                _query={"form_config": 1},
            ),
            "has_sepa_waiting_payments": has_waiting_payments(request),
        },
    }


class DeleteSepaWaitingPaymentView(DeleteView):
    delete_msg = "La facture est à nouveau en attente de paiement"

    def delete(self):
        if isinstance(self.context, ExpenseSepaWaitingPayment):
            return delete_sepa_waiting_payment_expense_sheet(self.request, self.context)

        else:
            return delete_supplier_invoice_sepa_waiting_payment(
                self.request, self.context
            )

    def redirect(self):
        if isinstance(self.context, ExpenseSepaWaitingPayment):
            return HTTPFound(
                self.request.route_path("/expenses/{id}", id=self.context.node_id)
            )
        else:
            return HTTPFound(
                self.request.route_path(
                    "/supplier_invoices/{id}", id=self.context.node_id
                )
            )


def cancel_sepa_credit_transfer_view(context, request):
    cancel_sepa_credit_transfer(request, context)
    return HTTPFound(request.route_path(SEPA_CREDIT_TRANSFER_COLLECTION_ROUTE))


def includeme(config):
    config.add_view(
        sepa_credit_transfer_entry_point_view,
        route_name=SEPA_CREDIT_TRANSFER_COLLECTION_ROUTE,
        layout="vue_opa",
        renderer="base/vue_app.mako",
        permission=PERMISSIONS["global.manage_accounting"],
    )
    config.add_view(
        DeleteSepaWaitingPaymentView,
        route_name=SEPA_WAITING_PAYMENT_ITEM_ROUTE,
        context=BaseSepaWaitingPayment,
        permission=PERMISSIONS["context.delete_sepa_waiting_payment"],
        require_csrf=True,
        request_method="POST",
    )
    config.add_view(
        cancel_sepa_credit_transfer_view,
        route_name=SEPA_CREDIT_TRANSFER_CANCEL_ROUTE,
        context=SepaCreditTransfer,
        renderer="/base/formpage.mako",
        request_method="POST",
        permission=PERMISSIONS["global.manage_accounting"],
    )
    config.add_admin_menu(
        parent="accounting",
        order=9,
        label="Ordre de virement SEPA",
        permission=PERMISSIONS["global.manage_accounting"],
        href=SEPA_CREDIT_TRANSFER_COLLECTION_ROUTE,
        routes_prefixes=[
            SEPA_CREDIT_TRANSFER_COLLECTION_ROUTE,
        ],
    )

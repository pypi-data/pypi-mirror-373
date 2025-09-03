from caerp.consts.permissions import PERMISSIONS
from caerp.models.task import Invoice
from caerp.utils.widgets import POSTButton
from caerp.views.business.business import BusinessOverviewView
from caerp.views.invoices.invoice import InvoiceGeneralView
from caerp.views.invoices.layout import InvoiceLayout

from caerp.views.task.utils import get_task_url


class InvoiceURSSAF3PLayout(InvoiceLayout):
    def _urssaf3p_request_action(self):
        return POSTButton(
            get_task_url(self.request, suffix="/urssaf3p_request"),
            label="Demander un paiement",
            title="Demander un paiement avec Avance Immédiate pour cette facture",
            icon="euro-sign",
            css="btn icon_only_mobile",
        )

    def stream_main_actions(self):
        if self.request.has_permission(
            PERMISSIONS["context.request_urssaf3p_invoice"], self.context
        ):
            yielded = False

            # Try to insert it after payment button
            for action in super().stream_main_actions():
                yield action
                if "payment" in action.url and not yielded:
                    yield self._urssaf3p_request_action()
                    yielded = True

            # But if we fail, show the button anyway
            if not yielded:
                yield self._urssaf3p_request_action()
        else:
            yield from super().stream_main_actions()


class URSSAF3PInvoiceGeneralView(InvoiceGeneralView):
    def get_urssaf_global_status(self):
        if self.context.urssaf_payment_request:
            urssaf_global_status = (
                self.context.urssaf_payment_request.urssaf_status_description
            )
        elif self.context.customer.urssaf_data:
            urssaf_customer_status = self.context.customer.urssaf_data.get_status()
            if urssaf_customer_status == "disabled":
                urssaf_global_status = (
                    "L'avance immédiate a été désactivée pour ce client"
                )
            elif urssaf_customer_status == "wait":
                urssaf_global_status = (
                    "En attente de la validation du client pour activer"
                    " l'avance immédiate"
                )
            elif urssaf_customer_status == "valid":
                urssaf_global_status = (
                    "Client inscrit à l'avance immédiate, demande de paiement possible"
                )
            else:
                urssaf_global_status = (
                    "Erreur de l'inscription du client au service d'avance immédiate"
                )
        else:
            urssaf_global_status = "Client non inscrit à l'avance immédiate"
        return urssaf_global_status

    def __call__(self):
        template_data = super().__call__()
        if not isinstance(template_data, dict):
            # Proabaly a HTTPFound or similar
            return template_data
        template_data["urssaf_global_status"] = self.get_urssaf_global_status()
        template_data["urssaf_payment_request"] = self.context.urssaf_payment_request
        return template_data


def includeme(config):
    config.add_layout(
        InvoiceURSSAF3PLayout,
        template="caerp:templates/tasks/invoice/layout.mako",
        name="invoice",
    )
    config.add_tree_view(
        URSSAF3PInvoiceGeneralView,
        parent=BusinessOverviewView,
        renderer="caerp:plugins/sap_urssaf3p/templates/tasks/invoice/general.mako",
        permission=PERMISSIONS["company.view"],
        context=Invoice,
        layout="invoice",
    )

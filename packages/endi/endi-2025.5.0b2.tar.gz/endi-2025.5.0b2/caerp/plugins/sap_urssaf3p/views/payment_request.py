import logging

from pyramid.httpexceptions import HTTPFound

from caerp.consts.permissions import PERMISSIONS
from caerp.utils.compat import Iterable
from caerp.models.task import Invoice
from caerp.models.status import StatusLogEntry
from caerp.plugins.sap_urssaf3p.models import URSSAFPaymentRequest
from caerp.plugins.sap_urssaf3p.serializers import serialize_invoice
from caerp.plugins.sap_urssaf3p.api_client import (
    get_urssaf_api_client,
    PermanentError,
    TemporaryError,
    HTTPBadRequest,
)
from caerp.views import BaseView
from caerp.views.task.utils import get_task_url


logger = logging.getLogger(__name__)


class InvoiceRequestController:
    def __init__(self, request):
        self.request = request

    def request_payment(self, invoice) -> str:
        """
        Enregistre la demande de paiement auprès de l'URSSAF

        :raises: TemporaryError in case of connection failed
        :raises: PermanentError in case of authentication / code (4xx/5xx...)

        :returns: le numéro de demande de paiement utilisé par l'URSSAF.
        """
        assert self.request.has_permission(
            PERMISSIONS["context.request_urssaf3p_invoice"], invoice
        )

        client = get_urssaf_api_client(self.request.registry.settings)
        serialized = serialize_invoice(invoice)
        urssaf_id = client.transmettre_demande_paiement(serialized)
        return urssaf_id

    @staticmethod
    def check_eligibility(invoice: Invoice) -> Iterable[str]:
        """Vérifie l'éligibilité d'une facture donnée au paiement via avance immédiate.

        :yields: les messages d'erreur, si il y en a.
        """
        preamble = "L'avance immmédiate de l'URSSAF ne supporte pas {}."
        if invoice.discounts:
            yield preamble.format("les remises")
        if invoice.total_ht() < 0:
            yield preamble.format("les avoirs")

        for line in invoice.all_lines:
            if line.total() < 0:
                yield preamble.format("les lignes négatives")
                break

    def historize_status(self, urssaf_request: URSSAFPaymentRequest) -> None:
        """Historise le statut de la demande de paiement auprès de l'URSSAF.

        :param URSSAFPaymentRequest urssaf_request: la demande de paiement auprès
        de l'URSSAF.
        """
        history = StatusLogEntry(
            node_id=urssaf_request.id,
            user_id=urssaf_request.request_status_user_id,
            comment=urssaf_request.request_comment,
            status=urssaf_request.request_status,
            datetime=urssaf_request.updated_at,
            state_manager_key="urssaf3p_request_status",
        )
        self.request.dbsession.add(history)
        self.request.dbsession.flush()

    def set_request_status(
        self,
        invoice: Invoice,
        user,
        status: str,
        comment="",
    ) -> URSSAFPaymentRequest:
        urssaf_request = invoice.urssaf_payment_request
        data_properties = dict(
            request_status=status,
            request_comment=comment,
            request_status_user_id=user.id,
            parent=invoice,
        )

        if not urssaf_request:
            urssaf_request = URSSAFPaymentRequest(**data_properties)
            invoice.urssaf_payment_request = urssaf_request
            self.request.dbsession.add(urssaf_request)
            self.request.dbsession.merge(invoice)
            self.request.dbsession.flush()
        else:
            for k, v in data_properties.items():
                setattr(urssaf_request, k, v)
            self.request.dbsession.merge(urssaf_request)

        self.historize_status(urssaf_request)
        return urssaf_request


class SAPInvoiceUrssaf3PAskView(BaseView):
    def __call__(self):
        invoice = self.request.context
        controller = InvoiceRequestController(request=self.request)
        blocked = False

        reasons = list(controller.check_eligibility(invoice))
        for blocking_reason in reasons:
            blocked = True
            self.session.flash(blocking_reason, queue="error")

        if blocked:
            self.session.flash(
                "Le paiement de cettte facture doit donc être géré "
                "sans l'avance immédiate de l'URSSAF.",
                queue="error",
            )
            logger.warning(
                f"Demande de paiement pour {invoice.official_number} "
                f"non soumise ({', '.join(reasons)})."
            )

        else:
            try:
                urssaf_id = controller.request_payment(invoice)
            except HTTPBadRequest as exc:
                self.session.flash(
                    f"Erreur renvoyée par l'URSSAF : {exc.code} - {exc.message}"
                    f" : {exc.description}",
                    queue="error",
                )
            except PermanentError:
                self.session.flash(
                    "Erreur permanente : il semble que l'accès d'enDI à l'API de l'URSSAF "
                    "soit mal configuré, veuillez contacter votre administrateuriii",
                    queue="error",
                )
            except TemporaryError:
                self.session.flash(
                    "Erreur temporaire de connexion à l'API de l'URSSAF, "
                    "veuillez ré-essayer plus tard",
                    queue="error",
                )
            else:
                msg = (
                    "Une demande de paiement a été envoyée à votre client. Son statut"
                    " sera mis à jour quotidiennement sur la page de la facture."
                )
                controller.set_request_status(
                    invoice,
                    self.request.identity,
                    URSSAFPaymentRequest.STATUS_WAITING,
                    msg,
                )

                invoice.urssaf_payment_request.urssaf_id = urssaf_id
                # asserted in client
                invoice.urssaf_payment_request.urssaf_status_code = "10"
                self.request.dbsession.merge(invoice.urssaf_payment_request)
                logger.info(
                    f"Demande de paiement pour {invoice.official_number}"
                    f" acceptée par l'API URSSAF (urssaf_id={urssaf_id})."
                )
                self.session.flash(msg)

        return self.redirect()

    def redirect(self):
        if self.request.referrer:
            url = self.request.referrer
        else:
            url = get_task_url(self.context)

        return HTTPFound(url)


def includeme(config):
    config.add_route(
        "/invoices/{id}/urssaf3p_request",
        r"/invoices/{id:\d+}/urssaf3p_request",
        traverse="/tasks/{id}",
    )
    config.add_view(
        SAPInvoiceUrssaf3PAskView,
        route_name="/invoices/{id}/urssaf3p_request",
        permission=PERMISSIONS["context.request_urssaf3p_invoice"],
        require_csrf=True,
        request_method="POST",
        context=Invoice,
    )

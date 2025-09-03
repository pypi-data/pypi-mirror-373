import dateutil.parser
import transaction
from datetime import date

from pyramid.request import Request
from pyramid_celery import celery_app
from pyramid.security import remember, forget
from celery.utils.log import get_task_logger

from caerp_base.mail import (
    send_mail,
    format_link,
)
from caerp_base.models import DBSESSION
from caerp_celery.hacks import setup_rendering_hacks
from caerp_celery.tasks import utils
from caerp.controllers.state_managers import check_node_resulted
from caerp.events.document_events import StatusChangedEvent
from caerp.export.task_pdf import ensure_task_pdf_persisted
from caerp.interfaces import IPaymentRecordService
from caerp.models.payments import BankAccount
from caerp.models.user import User
from caerp.plugins.sap_urssaf3p.api_client import (
    get_urssaf_api_client,
    TemporaryError,
)
from caerp.plugins.sap_urssaf3p.models.payment_request import URSSAFPaymentRequest
from caerp.plugins.sap_urssaf3p.models.services.payment_request import (
    URSSAFPaymentRequestService,
)
from caerp.utils.strings import format_account
from caerp.views.task.utils import get_task_url

logger = get_task_logger(__name__)


REQUEST_ERROR_MAIL_SUBJECT_TMPL = "{invoice_number} ({customer}) : Demande de paiement \
Avance Immédiate {request_status_title}"

REQUEST_ERROR_MAIL_BODY_TMPL = """\
Bonjour {username},

Nouveau statut pour la demande de paiement par Avance Immédiate pour la facture \
{invoice_number} ({invoice_label}) du dossier '{project}' avec le client {customer} :

{request_status_description}


Vous trouverez plus de détails sur la page de la facture : {invoice_url}"""


def get_urssaf3p_payment_bank_id(request):
    """
    Retourne l'id du compte bancaire à utiliser pour les encaissements
    automatiques d'avance immédiate
    """
    if request.config.get("urssaf3p_payment_bank_id"):
        return request.config.get("urssaf3p_payment_bank_id")
    else:
        default_bank_account = BankAccount.query().filter_by(default=True).first()
        if default_bank_account:
            return default_bank_account.id
        else:
            first_bank_account = BankAccount.query().first()
            if first_bank_account:
                return first_bank_account.id
            else:
                return None


def get_ongoing_requests_urssaf_ids() -> list:
    """
    Retourne les identifiants Urssaf de toutes les demandes de paiement
    qui ne sont pas terminées

    :return: Une liste d'identifiants Urssaf
    """
    ongoing_requests_urssaf_ids = []
    ongoing_requests = URSSAFPaymentRequest.query().filter_by(should_watch=True).all()
    for request in ongoing_requests:
        ongoing_requests_urssaf_ids.append(request.urssaf_id)
    return ongoing_requests_urssaf_ids


def send_payment_request_status_mail(request, registry, payment_request, status_code):
    """
    Envoi un mail à l'enseigne pour signaler un changement de statut sur une
    demande de paiement.
    """
    recipients = [payment_request.invoice.company.email]
    subject = REQUEST_ERROR_MAIL_SUBJECT_TMPL.format(
        invoice_number=payment_request.invoice.official_number,
        customer=payment_request.invoice.customer.label,
        request_status_title=URSSAFPaymentRequestService.get_title(status_code).lower(),
    )
    body = REQUEST_ERROR_MAIL_BODY_TMPL.format(
        username=format_account(payment_request.invoice.owner, reverse=False),
        invoice_number=payment_request.invoice.official_number,
        invoice_label=payment_request.invoice.internal_number.lower(),
        project=payment_request.invoice.project.name.capitalize(),
        customer=payment_request.invoice.customer.label,
        request_status_description=URSSAFPaymentRequestService.get_description(
            status_code
        ).lower(),
        invoice_url=format_link(
            registry.settings,
            get_task_url(
                request,
                payment_request.invoice,
                absolute=True,
            ),
        ),
    )
    send_mail(request, recipients, body, subject)


def generate_payment_from_request(
    pyramid_request: Request,
    urssaf_id: str,
    payment_date: date,
    payment_recovery=False,
) -> bool:
    """
    Génère l'encaissement correspondant au virement d'une demande de paiement

    :param pyramid_request: la requête Pyramid
    :param urssaf_id: l'identifiant Urssaf de la demande de paiement
    :param payment_date: date effective du paiement
    :param payment_recovery: est-ce que l'encaissement est un recouvrement ?
    :return: True si l'encaissement a bien été généré, False sinon
    """
    logger.info(f"Generating payment from payment request {urssaf_id}")

    # Récupération de la demande de paiement et la facture associée
    payment_request = URSSAFPaymentRequest.get_by_urssaf_id(urssaf_id)
    if not payment_request:
        logger.error(f"> Abort : No payment request with id {urssaf_id}")
        return False
    invoice = utils.get_task(payment_request.parent_id)
    if invoice is None:
        logger.error(f"> Abort : No invoice for payment request {urssaf_id}")
        return False

    try:
        # On attache l'utilisateur système (id=0) à la requête
        # pour qu'il soit l'origine de l'encaissement
        forget(pyramid_request)
        pyramid_request._cached_identity = None
        remember(pyramid_request, User.get(0).login.login)

        # On s'assure qu'on a bien un pdf dans le cache
        setup_rendering_hacks(pyramid_request, invoice)
        ensure_task_pdf_persisted(invoice, pyramid_request)

        # Enregistrement de l'encaissement
        payment_service = pyramid_request.find_service(IPaymentRecordService)
        payment_amount = invoice.ttc * -1 if payment_recovery else invoice.ttc
        payments = invoice.compute_payments(payment_amount)
        for payment in payments:
            tva_payment = {}
            tva_payment["date"] = payment_date
            tva_payment["amount"] = payment["amount"]
            tva_payment["tva_id"] = payment["tva_id"]
            tva_payment["mode"] = "Avance immédiate"
            tva_payment["bank_id"] = get_urssaf3p_payment_bank_id(pyramid_request)
            tva_payment["issuer"] = invoice.customer.label
            logger.debug(tva_payment)
            payment_service.add(invoice, tva_payment)
        check_node_resulted(pyramid_request, invoice)
        invoice.historize_paid_status(pyramid_request.identity)
        DBSESSION().merge(invoice)

        # Notification
        logger.info(
            f"> Payment generated for invoice {invoice.id} : amount={payment_amount}"
        )
        pyramid_request.registry.notify(
            StatusChangedEvent(
                pyramid_request,
                invoice,
                invoice.paid_status,
            )
        )

        DBSESSION().flush()
        transaction.commit()
        # REF #4053 : Dans la vie d'une requête HTTP qui n'a qu'une transaction on met
        # l'objet User en cache
        # Mais ici, on commite et ré-ouvre des transactions, le User en cache est celui
        # de la première transaction
        # Il génère donc des erreurs dans les suivantes
        # On l'oublie ce qui résoud le problème.
        forget(pyramid_request)
        pyramid_request._cached_identity = None
        return True
    except Exception:
        logger.exception("> Error in payment generation")
        transaction.abort()
        return False


def update_payments_from_api_data(request, api_data) -> bool:
    """
    Génère si nécessaire les encaissements relatifs à une demande de paiement
    à partir du retour de l'API de l'Urssaf

    :param request: la requête Pyramid
    :param api_data: l'objet JSON InfoDemandePaiement retourné par l'API
    :return: False en cas de problème, True sinon
    """
    urssaf_id = api_data["idDemandePaiement"]
    payment_request = URSSAFPaymentRequest.get_by_urssaf_id(urssaf_id)
    if payment_request is None:
        logger.error(f"No payment request with id {urssaf_id}")
        return False
    updated_status_code = api_data["statut"]["code"]
    try:
        payment_date = dateutil.parser.isoparse(
            api_data["infoVirement"]["dateVirement"]
        )
    except (KeyError, ValueError, TypeError):
        payment_date = date.today()

    # Si le nouveau statut est "payée" et qu'il ne l'était pas déjà
    # on génère l'encaissement
    if (
        URSSAFPaymentRequestService.get_caerp_status(updated_status_code) == "resulted"
        and payment_request.request_status != "resulted"
    ):
        return generate_payment_from_request(request, urssaf_id, payment_date)

    # Si la facture est recouvrée et qu'elle ne l'était pas déjà
    # on génère l'encaissement en négatif
    elif URSSAFPaymentRequestService.is_payment_recovery(
        updated_status_code
    ) and not URSSAFPaymentRequestService.is_payment_recovery(
        payment_request.urssaf_status_code
    ):
        return generate_payment_from_request(
            request, urssaf_id, payment_date, payment_recovery=True
        )


def update_payment_request_from_api_data(request, registry, api_data) -> bool:
    """
    Met à jour une demande de paiement à partir du retour de l'API de l'Urssaf

    :param request: la requête Pyramid
    :param api_data: l'objet JSON InfoDemandePaiement retourné par l'API
    :return: True si la demande a été mise à jour correctement, False sinon
    """
    urssaf_id = api_data["idDemandePaiement"]
    updated_status_code = api_data["statut"]["code"]
    logger.info(f"Updating payment request '{urssaf_id}' from API data")

    payment_request = URSSAFPaymentRequest.get_by_urssaf_id(urssaf_id)
    if payment_request is None:
        logger.error(f"> Abort : No payment request with id {urssaf_id}")
        return False

    try:
        original_status_code = payment_request.urssaf_status_code
        if payment_request.update_from_urssaf_status_code(updated_status_code):
            logger.info(
                "> Status updated : {} -> {}".format(
                    original_status_code, updated_status_code
                )
            )
            if (
                URSSAFPaymentRequestService.get_caerp_status(updated_status_code)
                == "aborted"
            ):
                # Si problème avec la demande de paiement on prévient l'entrepreneur
                send_payment_request_status_mail(
                    request, registry, payment_request, updated_status_code
                )
        if "infoRejet" in api_data:
            payment_request.update_from_reject_data(
                api_data["infoRejet"]["code"],
                api_data["infoRejet"].get("commentaire", ""),
            )
        if "infoVirement" in api_data:
            payment_request.update_from_transfer_data(
                api_data["infoVirement"]["dateVirement"],
                api_data["infoVirement"].get("mntVirement", None),
            )
        DBSESSION().merge(payment_request)
        DBSESSION().flush()
        transaction.commit()
        return True
    except Exception:
        logger.exception(f"> Error while updating payment request {urssaf_id}")
        transaction.abort()
        return False


# Celery task with auto-retry for temporary errors
@celery_app.task(bind=True, autoretry_for=(TemporaryError,), retry_backoff=True)
def check_urssaf3p_payment_requests(self):
    """
    Met à jour toutes les demandes de paiement en cours à partir des infos
    retournées par l'API de l'Urssaf
    """

    logger.info("Checking URSSAF payment requests...")

    pyramid_request = celery_app.conf["PYRAMID_REQUEST"]
    pyramid_registry = celery_app.conf["PYRAMID_REGISTRY"]

    payments_enabled = pyramid_request.config.get_value(
        "urssaf3p_automatic_payment_creation",
        default=False,
        type_=bool,
    )

    # Récupération des demandes de paiement en attente
    ongoing_requests_urssaf_ids = get_ongoing_requests_urssaf_ids()
    requests_count = len(ongoing_requests_urssaf_ids)
    if requests_count < 1:
        logger.info("> No ongoing requests - Abort process")
        return
    else:
        logger.info(
            "> {} ongoing payment requests - URSSAF IDs : {}".format(
                requests_count, ongoing_requests_urssaf_ids
            )
        )

    # Vérification des demandes en cours auprès de l'API de l'Urssaf
    urssaf3p_client = get_urssaf_api_client(pyramid_registry.settings)
    for i in range(0, requests_count, 10):
        ranged_requests_ids = ongoing_requests_urssaf_ids[i : i + 10]
        logger.info(
            "> Checking requests {} to {} ({})".format(i, i + 10, ranged_requests_ids)
        )
        response = urssaf3p_client.consulter_demandes(id_demandes=ranged_requests_ids)
        # Pour chaque retour de l'API on génère les encaissements si nécessaire
        # et on met à jour les demandes de paiement
        for infos_demande in response["infoDemandePaiements"]:
            if payments_enabled:
                update_payments_from_api_data(pyramid_request, infos_demande)
            update_payment_request_from_api_data(
                pyramid_request, pyramid_registry, infos_demande
            )

    logger.info("URSSAF payment requests checked !")

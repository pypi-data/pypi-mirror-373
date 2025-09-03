import logging
import typing

from caerp.exception import BadRequest
from caerp.models.task.payment import BankRemittance
from caerp.services.payment.invoice import get_bank_remittance

logger = logging.getLogger(__name__)

MESSAGES = {
    "old_remittance_closed": (
        "<strong>La remise en banque {remittance_id} a été clôturée.</strong>"
        "<br/><br/>Il n'est pas possible de modifier le numéro de "
        "remise en banque de cet encaissement car la remise a été clôturée."
        "<br/><br/>Vous pouvez remettre l'ancien numéro <strong>{remittance_id}"
        "</strong> ou rouvrir la remise depuis sa fiche : <a href='#' "
        "onclick=\"window.openPopup('{remittance_route}');\" title='Voir la remise "
        "dans une nouvelle fenêtre' aria-label='Voir la remise dans "
        "une nouvelle fenêtre'>Remise en banque {remittance_id}</a>"
    ),
    "remittance_unknown": (
        "<strong>La remise en banque {remittance_id} n'existe pas.</strong>"
        "<br/><br/>Vous pouvez confirmer la création de cette remise en "
        "cliquant sur le bouton ci-dessous ou modifier le numéro de la "
        "remise en banque.<br/><br/><button class='btn btn-primary' "
        "onclick=\"document.getElementsByName('new_remittance_confirm')[0]"
        ".value='true'; document.getElementById('deform').submit.click();\""
        "> Confirmer la création de cette remise et enregistrer "
        "l'encaissement</button>"
    ),
    "payment_bank": (
        "<strong>La remise en banque {remittance_id} ne correspond pas à cet "
        "encaissement.</strong><br/><br/>La remise en banque <strong>{remittance_id}"
        "</strong> existe déjà et est configurée pour le compte bancaire "
        "'<strong>{bank_label}</strong>' ; vous ne pouvez pas y adjoindre un "
        "paiement sur un autre compte.<br/><br/>Vous pouvez modifier "
        "le numéro de la remise en banque ou corriger le compte "
        "bancaire."
    ),
    "payment_mode": (
        "<strong>La remise en banque {remittance_id} ne correspond pas à cet "
        "encaissement.</strong><br/><br/>La remise en banque <strong>"
        "{remittance_id}</strong> existe déjà et est configurée pour "
        "le mode de paiement '<strong>{br.payment_mode}</strong>' ; vous "
        "ne pouvez pas y adjoindre un encaissement '<strong>{mode}</strong>'."
        "<br/><br/>Vous pouvez modifier le numéro de la remise en banque "
        "ou corriger le mode de paiement."
    ),
    "remittance_closed": (
        "<strong>La remise en banque {remittance_id} est déjà clôturée."
        "</strong><br/><br/>Vous pouvez modifier le numéro de la remise en "
        "banque ou rouvrir la remise depuis sa fiche : <a href='#' "
        "onclick=\"window.openPopup('{remittance_route}');\" "
        "title='Voir la remise "
        "dans une nouvelle fenêtre' aria-label='Voir la rermise "
        "dans une nouvelle fenêtre'>Remise en banque {remittance_id}</a>"
    ),
}


def check_remittance(
    request,
    remittance_id: str,
    mode: str,
    bank_id: int,
    old_remittance_id: typing.Optional[str] = None,
) -> typing.Optional[BankRemittance]:
    """
    Teste les informations saisies pour une remise en banque

    :raises BadRequest: Si une erreur connue est détectée
    """

    if old_remittance_id:
        br = get_bank_remittance(request, old_remittance_id)
        if not br:
            raise Exception("Ancienne remise en banque non trouvée")
        elif br.closed:
            remittance_route = request.route_path(
                "/accounting/bank_remittances/{id}", id=remittance_id
            )
            message = MESSAGES["old_remittance_closed"].format(
                remittance_id=old_remittance_id,
                remittance_route=remittance_route,
            )
            raise BadRequest(message=message)

    br = get_bank_remittance(request, remittance_id)
    if br:
        if br.payment_mode == mode and br.bank_id == bank_id:  # noqa
            if br.closed:
                message = MESSAGES["remittance_closed"].format(
                    remittance_id=remittance_id,
                    remittance_route=request.route_path(
                        "/accounting/bank_remittances/{id}", id=remittance_id
                    ),
                )
                raise BadRequest(message=message)
        else:
            # Erreur : mode de paiement ou banque ne correspondent pas
            if br.payment_mode != mode:
                raise BadRequest(
                    message=MESSAGES["payment_mode"].format(
                        remittance_id=remittance_id,
                        br=br,
                        mode=mode,
                    )
                )
            if br.bank_id != bank_id:
                if br.bank:
                    bank_label = br.bank.label
                else:
                    bank_label = "-NON DEFINI-"
                raise BadRequest(
                    message=MESSAGES["payment_bank"].format(
                        remittance_id=remittance_id,
                        br=br,
                        bank_label=bank_label,
                    )
                )
    return br


def format_bank_remittance_name(request, remittance_id: str):
    """Format the bank remittance name to exclude forbidden characters"""
    return remittance_id.replace("/", "_")


def create_bank_remittance(
    request, remittance_id: str, mode: str, bank_id: int
) -> BankRemittance:
    """
    Create a new bank remittance in the database

    :raises AssertionError: Si une remise en banque existe déjà
    """
    # On ajoute un assert pour éviter la création d'une remise en banque qui existe déjà
    assert get_bank_remittance(request, remittance_id) is None

    result = BankRemittance(id=remittance_id, payment_mode=mode, bank_id=bank_id)
    request.dbsession.add(result)
    request.dbsession.flush()
    logger.info("New bank remittance: '%s' added", remittance_id)
    return result

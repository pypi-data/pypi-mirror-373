import datetime
import logging
from dataclasses import dataclass

import dateutil.parser
from sqlalchemy import and_
from typing import Optional


logger = logging.getLogger(__name__)


@dataclass
class RequestStatus:
    urssaf_status_code: str
    title: str
    description: str
    caerp_status: str
    payment_recovery: bool = False


@dataclass
class RejectStatus:
    code: str
    category: str
    label: str


class URSSAFPaymentRequestService:
    """
    Cf Documentation-API-TiersPrestation_v1-1-7.pdf
    - 4.3 Statuts de la demande de paiement
    - 3.3.3 Description de la réponse
    """

    STATUSES = [
        RequestStatus(
            urssaf_status_code="10",
            title="Intégrée",
            description=(
                "La demande de paiement a été reçue et acceptée par l'URSSAF."
            ),
            caerp_status="waiting",
        ),
        RequestStatus(
            urssaf_status_code="20",
            title="En attente de validation",
            description=(
                "Le client a été prévenu qu'il doit valider ou rejeter"
                " la demande de paiement."
            ),
            caerp_status="waiting",
        ),
        RequestStatus(
            urssaf_status_code="30",
            title="Validée",
            description=(
                "La demande de paiement a été validée par le client et"
                " le prélèvement a été initié."
            ),
            caerp_status="waiting",
        ),
        RequestStatus(
            urssaf_status_code="40",
            title="Refusée",
            description=("La demande de paiement a été refusée par le client."),
            caerp_status="aborted",
        ),
        RequestStatus(
            urssaf_status_code="50",
            title="Prélevée",
            description=("Le prélèvement de la demande de paiement est en cours."),
            caerp_status="waiting",
        ),
        RequestStatus(
            urssaf_status_code="60",
            title="En refus de prélèvement",
            description=(
                "Le prélèvement de la demande de paiement est revenu en erreur."
                "La demande de paiement est en impayé."
            ),
            caerp_status="payment_issue",
        ),
        RequestStatus(
            urssaf_status_code="70",
            title="Payée",
            description=("La demande de paiement a été payée au prestataire."),
            caerp_status="resulted",
        ),
        RequestStatus(
            urssaf_status_code="110",
            title="Annulée",
            description=(
                "La demande de paiement a été annulée suite à une demande"
                " motivée du prestataire."
            ),
            caerp_status="aborted",
        ),
        RequestStatus(
            urssaf_status_code="111",
            title="Annulée après impayé",
            description=(
                "La demande de paiement a été annulée après impayé du client."
            ),
            caerp_status="aborted",
        ),
        RequestStatus(
            urssaf_status_code="112",
            title="Annulée après recouvrement",
            description=(
                "La demande de paiement a été annulée après recouvrement par le "
                "prestataire."
            ),
            caerp_status="aborted",
            payment_recovery=True,
        ),
        RequestStatus(
            urssaf_status_code="120",
            title="Recouvrée",
            description=(
                "La demande de paiement en impayé a été recouvrée par le prestataire."
            ),
            caerp_status="aborted",
            payment_recovery=True,
        ),
    ]
    URSSAF_MAP = {ps.urssaf_status_code: ps for ps in STATUSES}

    REJECT_STATUSES = [
        RejectStatus(
            code="REGUL_MNT_FACT",
            category="Régularisation",
            label="Erreur sur le montant facturé et/ou sur le tarif indiqué pour la prestation",
        ),
        RejectStatus(
            code="REGUL_NB_QTE_FACT",
            category="Régularisation",
            label="Nombre d'heures ou quantités facturées erronées",
        ),
        RejectStatus(
            code="REGUL_PRESTA_FACT",
            category="Régularisation",
            label="Erreur sur les prestations facturées",
        ),
        RejectStatus(
            code="REGUL_AUTRE",
            category="Régularisation",
            label="Autre motif",
        ),
        RejectStatus(
            code="CONTEST_ERR_FACT",
            category="Contestation",
            label="La facture comporte une erreur",
        ),
        RejectStatus(
            code="CONTEST_FACT_REGLEE",
            category="Contestation",
            label="La facture a déjà été réglée",
        ),
        RejectStatus(
            code="CONTEST_AUTRE",
            category="Contestation",
            label="Autre motif",
        ),
        RejectStatus(
            code="ANNUL_DBL",
            category="Annulation",
            label="Demande de paiement en doublon",
        ),
        RejectStatus(
            code="ANNUL_ERR_MNT",
            category="Annulation",
            label="Montant facturé erroné",
        ),
        RejectStatus(
            code="ANNUL_ERR_TECH",
            category="Annulation",
            label="Erreur technique",
        ),
        RejectStatus(
            code="ANNUL_AUTRE",
            category="Annulation",
            label="Autre motif",
        ),
    ]
    REJECT_MAP = {rs.code: rs for rs in REJECT_STATUSES}

    # FIXME: à ajuster en fonction du retour de l'URSSAF :
    WATCHING_DELAY = datetime.timedelta(days=7)

    @classmethod
    def get_caerp_status(cls, urssaf_status_code: str) -> str:
        try:
            return cls.URSSAF_MAP[urssaf_status_code].caerp_status
        except KeyError:
            logger.error(f"URSSAF status code {urssaf_status_code} unknown")
            return "unknown"

    @classmethod
    def get_description(cls, urssaf_status_code: str) -> str:
        try:
            return cls.URSSAF_MAP[urssaf_status_code].description
        except KeyError:
            return ""

    @classmethod
    def get_title(cls, urssaf_status_code: str) -> str:
        try:
            return cls.URSSAF_MAP[urssaf_status_code].title
        except KeyError:
            return "Inconnu"

    @classmethod
    def get_reject_label(cls, reject_status_code: str) -> str:
        try:
            return "Rejet pour {} : {}".format(
                cls.REJECT_MAP[reject_status_code].category.lower(),
                cls.REJECT_MAP[reject_status_code].label,
            )
        except KeyError:
            return "Rejet pour motif inconnu"

    @classmethod
    def should_watch_property(cls, obj: "URSSAFPaymentRequest") -> bool:
        """
        Should we continue to watch this request against the URSSAF_API

        checking the status is not enough since « paid » status can be or not a final status
        """
        min_dt = datetime.datetime.now() - cls.WATCHING_DELAY
        return (obj.request_status not in obj.FINAL_STATUSES) and (
            obj.updated_at > min_dt
        )

    @classmethod
    def should_watch_expression(service, cls):
        # sqla mapping of timedelta to mariadb is wrong (Mapped to DATETIME),
        # Thus, this code avoids sending timedelta objects to SQLA.
        min_dt = datetime.datetime.now() - service.WATCHING_DELAY
        return and_(
            cls.request_status.not_in(cls.FINAL_STATUSES),
            cls.updated_at > min_dt,
        )

    @classmethod
    def update_from_urssaf_status_code(
        cls, urssaf_status_code: str, obj: "URSSAFPaymentRequest"
    ) -> bool:
        """
        Mutate URSSAF payment request after receiving a new status code from URSSAF

        :return: True if this was a new status and obj was updated.
        """
        if obj.urssaf_status_code != urssaf_status_code:
            obj.request_comment = cls.get_description(urssaf_status_code)
            obj.request_status = cls.get_caerp_status(urssaf_status_code)
            obj.urssaf_status_code = urssaf_status_code
            return True
        else:
            return False

    @classmethod
    def update_from_reject_data(
        cls, reject_code: str, reject_comment: str, obj: "URSSAFPaymentRequest"
    ) -> bool:
        """
        Mutate URSSAF payment request after receiving reject data

        :return: True if obj was updated
        """
        reject_label = cls.get_reject_label(reject_code)
        if reject_label != "Inconnu":
            obj.urssaf_reject_message = f"""
            {reject_label}

            Message : {reject_comment}
            """
            return True
        else:
            return False

    @classmethod
    def update_from_transfer_data(
        cls,
        obj: "URSSAFPaymentRequest",
        transfer_date: str,
        transfer_amount: Optional[str] = None,
    ) -> bool:
        """
        Mutate URSSAF payment request after receiving transfer data

        :return: True if obj was updated
        """
        transfer_dt = dateutil.parser.isoparse(transfer_date)
        if transfer_amount is None:
            # Dans les faits, même si non documenté, le transfer_amount est,
            # à date du 23/11/2023, retourné vide par l'API URSSAF au stade ou le
            # virement est programmé mais non effectif.
            obj.urssaf_transfer_message = "Virement au prestataire prévu le {}".format(
                transfer_dt.strftime("%d/%m/%Y"),
            )
        else:
            obj.urssaf_transfer_message = (
                "Virement au prestataire de {}€ effectué le {}".format(
                    transfer_amount,
                    transfer_dt.strftime("%d/%m/%Y"),
                )
            )
        return True

    @classmethod
    def is_payment_recovery(cls, urssaf_status_code: str) -> bool:
        return cls.URSSAF_MAP[urssaf_status_code].payment_recovery

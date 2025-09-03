import logging

from sqlalchemy import Column, String, Integer

from caerp_base.models.base import (
    DBBASE,
    default_table_args,
)

logger = logging.getLogger(__name__)


class GeneralLedgerAccountWording(DBBASE):
    """
    Model storing correspondences between account number and wording
    to display in the general ledger view
    :param account_number: account number
    :param wording: corresponding wording
    """

    __colanderalchemy_config__ = {
        "title": "Nom des numéros de comptes du grand livre",
        "validation_msg": "Les modifications ont bien été enregistrés",
        "help_msg": "Permet de rendre plus lisible le Grand Livre pour les\
        entrepreneurs",
    }
    __tablename__ = "general_ledger_account_wording"
    __table_args__ = default_table_args

    id = Column(Integer, primary_key=True, info={"colanderalchemy": {"exclude": True}})
    account_number = Column(
        String(20),
        nullable=False,
        info={
            "colanderalchemy": {
                "title": "Numéro de compte",
            }
        },
    )
    wording = Column(  # active means closed
        String(100),
        nullable=False,
        info={
            "colanderalchemy": {
                "title": "Nom du compte du Grand Livre",
            }
        },
    )

    def __json__(self, request=None):
        return {
            "id": self.id,
            "account_number": self.account_number,
            "wording": self.wording,
        }

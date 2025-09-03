import typing

from caerp.models.task import BankRemittance
from caerp.services import get_model_by_id


def get_bank_remittance(
    request, bank_remittance_id: str
) -> typing.Optional[BankRemittance]:
    """
    Retrieve a bank remittance from the database based on its ID.

    Args:
        request (pyramid.request.Request): The current request.
        bank_remittance_id (int): The ID of the bank remittance to retrieve.

    Returns:
        caerp.models.bank_remittance.BankRemittance: The bank remittance object.
        None: If the bank remittance with the given ID does not exist.
    """

    return get_model_by_id(request, BankRemittance, bank_remittance_id)

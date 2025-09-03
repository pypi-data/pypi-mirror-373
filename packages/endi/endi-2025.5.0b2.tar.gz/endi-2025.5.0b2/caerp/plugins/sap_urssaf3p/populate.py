from sqlalchemy import func

from caerp.models.populate import PopulateRegistry


def populate_sap_urssaf3p_payment_mode(session):
    from caerp.models.payments import PaymentMode

    urssaf3p_payment_mode = "Avance immédiate"
    query = session.query(PaymentMode).filter(
        func.lower(PaymentMode.label) == func.lower(urssaf3p_payment_mode)
    )
    if query.count() == 0:
        session.add(PaymentMode(label=urssaf3p_payment_mode))
    session.flush()


def populate_sap_urssaf3p_config(session):
    """
    Payment creation is enabled by default
    """
    from caerp.models.config import Config

    key = "urssaf3p_automatic_payment_creation"
    if Config.get(key) is None:
        Config.set(key, "1")
    session.flush()


def includeme(config):
    PopulateRegistry.add_function(populate_sap_urssaf3p_payment_mode)
    PopulateRegistry.add_function(populate_sap_urssaf3p_config)

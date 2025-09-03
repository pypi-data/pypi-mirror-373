import logging
import os

from pyramid.httpexceptions import HTTPNotFound
from pyramid_mailer.message import Message

from caerp.models.company import Company
from caerp.models.smtp import SmtpSettings
from caerp.services.company import get_company_by_id
from caerp.services.smtp.smtp import (
    get_fernet_for_smtp_password,
    get_mailer_from_smtp_settings,
    get_smtp_by_company_id,
    get_smtp_by_id,
)

logger = logging.getLogger(__name__)


def _hash_smtp_password(request, derivation_salt, smtp_password):
    """Hash the given SMTP password for db storage"""
    fernet = get_fernet_for_smtp_password(request, derivation_salt)
    hashed_password = fernet.encrypt(smtp_password.encode())
    return hashed_password.decode()


def create_smtp_settings(
    request,
    smtp_host,
    smtp_port,
    smtp_user,
    smtp_password,
    sender_email,
    smtp_ssl=False,
    smtp_tls=False,
    company_id=None,
):
    """Create a new SmtpSettings instance."""
    settings = get_smtp_by_company_id(request, company_id)
    if settings:
        return update_smtp_settings(
            request,
            settings.id,
            smtp_host,
            smtp_port,
            smtp_user,
            smtp_password,
            sender_email,
            smtp_ssl,
            smtp_tls,
        )

    smtp_salt = os.urandom(16).hex()
    hashed_smtp_password = _hash_smtp_password(request, smtp_salt, smtp_password)

    smtp_settings = SmtpSettings(
        smtp_host=smtp_host,
        smtp_port=smtp_port,
        smtp_user=smtp_user,
        smtp_password_salt=smtp_salt,
        smtp_password_hash=hashed_smtp_password,
        smtp_ssl=smtp_ssl,
        smtp_tls=smtp_tls,
        sender_email=sender_email,
        company_id=company_id,
    )
    company = request.dbsession.query(Company).filter(Company.id == company_id).first()
    if company:
        company.smtp_configuration = "company"
        request.dbsession.merge(company)
    request.dbsession.add(smtp_settings)

    request.dbsession.flush()
    return smtp_settings


def update_smtp_settings(
    request,
    smtp_settings_id,
    smtp_host,
    smtp_port,
    smtp_user,
    sender_email,
    smtp_password=None,
    smtp_ssl=False,
    smtp_tls=False,
):
    setting = get_smtp_by_id(request, smtp_settings_id)
    if setting:
        setting.smtp_host = smtp_host
        setting.smtp_port = smtp_port
        setting.smtp_user = smtp_user
        setting.smtp_ssl = smtp_ssl
        setting.smtp_tls = smtp_tls
        setting.sender_email = sender_email

        if smtp_password:
            smtp_salt = setting.smtp_password_salt
            hashed_smtp_password = _hash_smtp_password(
                request, smtp_salt, smtp_password
            )
            setting.smtp_password_hash = hashed_smtp_password
        request.dbsession.merge(setting)
        request.dbsession.flush()
    else:
        raise HTTPNotFound("Smtp settings not found")
    return setting


def delete_smtp_settings(request, smtp_settings: SmtpSettings):
    company = get_company_by_id(request, smtp_settings.company_id)
    if company:
        company.smtp_configuration = "none"
        request.dbsession.merge(company)
    request.dbsession.delete(smtp_settings)


def send_test_email(request, smtp_settings: SmtpSettings, recipient_email: str):
    """
    Envoi un email de test à l'aide des smtpsettings fournies

    :raises: Exception si une erreur survient lors de l'envoi du mail
    """

    mailer = get_mailer_from_smtp_settings(request, smtp_settings)
    message = Message(
        subject="Test d’envoi d’e-mail depuis enDI",
        sender=f"enDI<{smtp_settings.sender_email}",
        recipients=[recipient_email],
        body="Ceci est un e-mail de test envoyé depuis enDI.",
    )
    try:
        mailer.send_immediately(message)
    except Exception as e:
        logger.exception(f"Error sending test email to {recipient_email}")
        raise e

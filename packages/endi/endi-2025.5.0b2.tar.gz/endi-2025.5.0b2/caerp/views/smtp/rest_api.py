import logging

import colander
from sqlalchemy import select

from caerp.consts.permissions import PERMISSIONS
from caerp.controllers.smtp.settings import (
    create_smtp_settings,
    delete_smtp_settings,
    send_test_email,
    update_smtp_settings,
)
from caerp.forms.jsonschema import convert_to_jsonschema
from caerp.forms.smtp.settings import get_add_edit_smtp_settings_schema
from caerp.models.company import Company
from caerp.models.smtp import SmtpSettings
from caerp.services.smtp.smtp import (
    get_cae_smtp,
    get_smtp_by_company_id,
    smtp_settings_to_json,
)
from caerp.utils import rest
from caerp.views import BaseRestView

from .routes import (
    API_BASE_ROUTE,
    API_COMPANY_SMTP_ROUTE,
    API_COMPANY_TESTMAIL_ROUTE,
    API_ITEM_ROUTE,
    TEST_MAIL_ROUTE,
)

logger = logging.getLogger(__name__)


class SmtpSettingsRestView(BaseRestView):
    def __init__(self, context, request=None):
        super().__init__(context, request)
        smtp_settings = self.get_current_smtp_settings()
        if smtp_settings is not None:
            self.edit = True
        else:
            self.edit = False

    def get_current_smtp_settings(self):
        if isinstance(self.context, SmtpSettings):
            return self.context
        elif isinstance(self.context, Company):
            return get_smtp_by_company_id(self.request, self.context.id)
        else:
            return get_cae_smtp(self.request)

    def format_item_result(self, model) -> dict:
        return smtp_settings_to_json(self.request, model)

    def collection_get(self):
        return self.request.dbsession.execute(select(SmtpSettings)).scalars().all()

    def get_schema(self, submitted_data):
        return get_add_edit_smtp_settings_schema(edit=self.edit)

    def get_company_id(self):
        if isinstance(self.context, Company):
            return self.context.id
        return None

    def _add_element(self, schema, attributes):
        """
        Context is Company (company smtp) or RootFactory (Cae Smtp)
        """
        return create_smtp_settings(
            request=self.request, company_id=self.get_company_id(), **attributes
        )

    def _edit_element(self, schema, attributes):
        """
        Context is a SmtpSettings instance
        """
        if isinstance(self.context, SmtpSettings):
            settings_id = self.context.id
        else:
            settings_id = attributes.pop("id", None)
        assert settings_id is not None
        return update_smtp_settings(self.request, settings_id, **attributes)

    def form_config(self):
        return {
            "schemas": {"default": convert_to_jsonschema(self.get_schema({}))},
            "options": {
                "can_send_test_email": bool(self.request.identity.email),
            },
        }

    def test_email_view(self):
        logger.debug("Envoi d'un e-mail de test")
        data = self.request.json_body
        schema = self.get_schema(data)
        schema = schema.bind(request=self.request)

        try:
            attributes = schema.deserialize(data)
        except colander.Invalid as err:
            self.logger.exception("  - Erreur")
            raise rest.RestError(err.asdict(), 400)
        else:
            try:
                if data.get("id"):
                    logger.debug("Edition d'un enregistrement")
                    smtp_settings = update_smtp_settings(
                        self.request, data["id"], **attributes
                    )
                    logger.debug("Enregistrement modifié avec succès")
                    logger.debug(smtp_settings)

                else:
                    logger.debug("Ajout d'un enregistrement")
                    smtp_settings = self._add_element(schema, attributes)
                recipient_email = self.request.identity.email
                assert recipient_email
                logger.debug(f"Envoi de l'email à {recipient_email}")
                send_test_email(
                    self.request, smtp_settings, recipient_email=recipient_email
                )
                return {
                    "status": "success",
                    "message": "L'e-mail de test a été envoyé avec succès.",
                }
            except AssertionError:
                logger.exception("Votre compte n'a pas d'e-mail renseigné.")
                return {
                    "status": "danger",
                    "message": "Votre compte n'a pas d'e-mail renseigné.",
                }
            except Exception as e:
                logger.exception(
                    "Une erreur est survenue lors de l'envoi de l'e-mail de test."
                )
                return {
                    "status": "danger",
                    "message": (
                        f"Une erreur est survenue lors de l'envoi de l'e-mail de "
                        f"test {e}."
                    ),
                }

    def delete(self):
        delete_smtp_settings(self.request, self.context)
        return {}


def includeme(config):
    """
    Include SMTP settings REST views in the Pyramid configuration.
    """
    config.add_rest_service(
        SmtpSettingsRestView,
        route_name=API_ITEM_ROUTE,
        collection_route_name=API_BASE_ROUTE,
        context=SmtpSettings,
        collection_view_rights=PERMISSIONS["global.config_cae"],
        add_rights=PERMISSIONS["global.config_cae"],
        view_rights=PERMISSIONS["context.view"],
        edit_rights=PERMISSIONS["context.edit"],
        delete_rights=PERMISSIONS["context.edit"],
    )
    config.add_view(
        SmtpSettingsRestView,
        route_name=TEST_MAIL_ROUTE,
        request_method="POST",
        attr="test_email_view",
        permission=PERMISSIONS["global.config_cae"],
        renderer="json",
    )

    config.add_view(
        SmtpSettingsRestView,
        route_name=API_BASE_ROUTE,
        attr="form_config",
        request_param="form_config",
        renderer="json",
        permission=PERMISSIONS["global.config_cae"],
    )

    config.add_view(
        SmtpSettingsRestView,
        route_name=API_COMPANY_SMTP_ROUTE,
        attr="form_config",
        request_param="form_config",
        renderer="json",
        permission=PERMISSIONS["company.view"],
    )
    config.add_rest_service(
        SmtpSettingsRestView,
        collection_route_name=API_COMPANY_SMTP_ROUTE,
        context=SmtpSettings,
        collection_view_rights=PERMISSIONS["company.view"],
        add_rights=PERMISSIONS["company.view"],
    )
    config.add_view(
        SmtpSettingsRestView,
        route_name=API_COMPANY_TESTMAIL_ROUTE,
        request_method="POST",
        attr="test_email_view",
        permission=PERMISSIONS["company.view"],
        renderer="json",
    )

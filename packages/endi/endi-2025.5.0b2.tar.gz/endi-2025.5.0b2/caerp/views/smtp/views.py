import logging

from pyramid.httpexceptions import HTTPFound

from caerp.consts.permissions import PERMISSIONS
from caerp.controllers.smtp.task import send_task_to_customer
from caerp.forms.smtp.mail_node import get_send_mail_schema
from caerp.models.company import Company
from caerp.models.task.task import Task
from caerp.resources import smtp_settings_js
from caerp.services.smtp.smtp import (
    get_company_smtp_by_company_id,
    get_smtp_by_company_id,
)
from caerp.services.smtp.task import (
    get_default_task_mail_body,
    get_default_task_mail_subject,
)
from caerp.utils.strings import format_task_type
from caerp.views import BaseFormView, BaseView, JsAppViewMixin, TreeMixin
from caerp.views.smtp.routes import (
    API_BASE_ROUTE,
    API_COMPANY_SMTP_ROUTE,
    COMPANY_SMTP_SETTINGS_ROUTE,
    SEND_MAIL_ROUTE,
)
from caerp.views.task.utils import get_task_url

logger = logging.getLogger(__name__)


class CompanySmtpSettingsView(BaseView, JsAppViewMixin, TreeMixin):
    """
    SMTP settings view
    """

    route_name = COMPANY_SMTP_SETTINGS_ROUTE
    title = "Serveur du service d’envoi d’e-mails"

    def get_company_id(self):
        return self.context.id

    def context_url(self, _query):
        return self.request.route_path(self.route_name, id=self.context.id)

    def get_api_url(self):
        return self.request.route_url(API_COMPANY_SMTP_ROUTE, id=self.context.id)

    def get_current_smtp_settings(self):
        return get_smtp_by_company_id(self.request, self.context.id)

    def get_js_app_options(self):
        result = {
            "api_url": self.get_api_url(),
            "company_id": self.get_company_id(),
            "smtp_settings_id": None,
            "form_config_url": self.request.route_path(
                API_BASE_ROUTE, _query={"form_config": 1}
            ),
        }
        logger.debug(self.context)
        current_smtp_settings = self.get_current_smtp_settings()
        if current_smtp_settings:
            result["smtp_settings_id"] = current_smtp_settings.id
        elif self.get_company_id() is not None:
            result["default_email"] = self.request.identity.email
        return result

    def __call__(self) -> dict:
        smtp_settings_js.need()
        self.populate_navigation()
        return {
            "title": self.title,
            "js_app_options": self.get_js_app_options(),
        }


"""
1- Renvoyer le formulaire avec : 
    - la description des informations sur le service d’envoi d’e-mails
    - l'adresse mail du destinataire 
    - l'objet par défaut du mail
    - le message par défaut

2- Récupérer les informations du formulaire 
3- Récupérer le controller à utiliser pour envoyer le mail
4- Updater l'e-mail du client
"""


class SendNodeMailView(BaseFormView):
    """
    Send node mail view

    context : Node
    """

    def get_schema(self):
        return get_send_mail_schema(self.request, self.context)

    def get_defaults(self):
        return {}

    def before(self, form):
        form.set_appstruct(self.get_defaults())

    def redirect(self):
        return "/"

    def submit_success(self, appstruct):
        send_options = {
            "body": appstruct["body"],
            "subject": appstruct["subject"],
            "recipient_email": appstruct["recipient_email"],
            "copy_to": appstruct.get("copy_to"),
            "reply_to": appstruct.get("reply_to"),
        }
        try:
            send_task_to_customer(self.request, self.context, **send_options)
            self.context.sent_by_email = True
            self.request.dbsession.merge(self.context)
        except Exception as e:
            logger.error(f"Error while sending mail: {e}")
            self.request.session.flash(
                f"Erreur lors de l’envoi de l’e-mail: {e}", queue="error"
            )
        else:
            self.request.session.flash("E-mail envoyé avec succès", queue="success")

        try:
            if appstruct["save_recipient"]:
                self.context.customer.email = appstruct["recipient_email"]
                self.request.dbsession.merge(self.context.customer)
                self.request.dbsession.flush()
        except Exception as e:
            logger.error(f"Error while saving recipient email: {e}")
            self.request.session.flash(
                f"Erreur lors de la sauvegarde de l’adresse mail du client : {e}",
                queue="error",
            )
        return HTTPFound(self.redirect())


class SendTaskMailView(SendNodeMailView):
    add_template_vars = ("help_message",)

    @property
    def help_message(self):
        smtp_settings = get_company_smtp_by_company_id(
            self.request, self.context.company_id
        )
        logger.debug(f"SMTP settings: {smtp_settings}")
        return (
            f"L’e-mail sera envoyé depuis l’adresse "
            f'<pre>"{self.context.company.name}"'
            f"&lt;{smtp_settings.sender_email}&gt;</pre>"
        )

    @property
    def title(self):
        label = format_task_type(self.context)
        if self.context.official_number:
            number = self.context.official_number
        else:
            number = self.context.internal_number
        return (
            f"{label} {number} : envoi par e-mail au client "
            f"{self.context.customer.label}"
        )

    def get_defaults(self):
        copy_to = []
        company = self.context.company
        if company.smtp_configuration == "cae":
            if company.email is not None:
                copy_to.append(self.context.company.email)
            else:
                copy_to.append(self.request.identity.email)

        result = {
            "recipient_email": self.context.customer.email,
            "subject": get_default_task_mail_subject(self.request, self.context),
            "body": get_default_task_mail_body(self.request, self.context),
            "copy_to": ",".join(copy_to),
        }
        smtp_settings = get_company_smtp_by_company_id(
            self.request, self.context.company_id
        )

        if company.email is not None:
            if smtp_settings.sender_email != company.email:
                result["reply_to"] = company.email
        elif smtp_settings.sender_email != self.request.identity.email:
            result["reply_to"] = self.request.identity.email
        return result

    def redirect(self):
        task_url = get_task_url(self.request, suffix="/general")
        return task_url


def includeme(config):
    config.add_view(
        CompanySmtpSettingsView,
        route_name=COMPANY_SMTP_SETTINGS_ROUTE,
        layout="vue_opa",
        context=Company,
        permission=PERMISSIONS["context.edit_company"],
        renderer="base/vue_app.mako",
    )
    config.add_view(
        SendTaskMailView,
        route_name=SEND_MAIL_ROUTE,
        context=Task,
        permission=PERMISSIONS["company.view"],
        renderer="base/formpage.mako",
    )

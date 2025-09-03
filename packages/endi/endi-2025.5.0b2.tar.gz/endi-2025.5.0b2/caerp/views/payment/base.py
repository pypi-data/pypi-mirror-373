import logging

from pyramid.httpexceptions import HTTPFound

from caerp.controllers.state_managers.payment import check_node_resulted
from caerp.views import (
    BaseEditView,
    BaseView,
    PopupMixin,
    TreeMixin,
    cancel_btn,
    submit_btn,
)

logger = logging.getLogger(__name__)


def get_delete_confirm_message(
    context, payment_label="paiement", payment_label_prefix="ce"
):
    if context.exported:
        return (
            f"Attention : {payment_label_prefix.capitalize()} {payment_label}"
            f"a déjà été exporté en comptabilité !\n"
            f"Si vous le supprimez, pensez à modifier manuellement les"
            f" écritures associées dans votre logiciel de comptabilité. \n"
            f"Êtes-vous sûr de vouloir supprimer {payment_label_prefix} "
            f"{payment_label} ?"
        )
    else:
        return (
            f"Êtes-vous sûr de vouloir supprimer {payment_label_prefix} "
            f"{payment_label}?"
        )


def get_warning_message(context, payment_label="paiement", payment_label_prefix="ce"):
    if context.exported:
        return (
            f"{payment_label_prefix} {payment_label} a déjà été exporté en comptabilité, si"
            f" vous le modifiez, pensez à modifier les"
            f" écritures associées dans votre logiciel de comptabilité. \n"
        )


class BasePaymentEditView(BaseEditView, TreeMixin):
    """
    Edit payment view
    """

    add_template_vars = ("warn_message",)
    title = "Modification d'un paiement"
    buttons = (
        submit_btn,
        cancel_btn,
    )

    def before(self, form):
        form.set_appstruct(self.context.appstruct())
        self.populate_navigation()

    def get_default_redirect(self):
        """
        Get the default redirection path
        """
        return self.request.route_path("payment", id=self.context.id)

    def edit_payment(self, appstruct):
        """
        Edit the payment object, handles form datas persistence
        """
        raise NotImplementedError("Method edit_payment not implemented")

    def after_parent_save(self, parent):
        pass

    def merge_appstruct(self, appstruct, model):
        force_resulted = appstruct.pop("resulted", False)

        payment = self.edit_payment(appstruct)
        # Met à jour le statut de paiement du parent
        parent = payment.parent
        parent = check_node_resulted(
            self.request,
            payment.parent,
            force_resulted=force_resulted,
        )
        self.dbsession.merge(parent)
        self.after_parent_save(parent)
        return payment

    def redirect(self, appstruct):
        come_from = appstruct.pop("come_from", None)
        if come_from is not None:
            redirect = come_from
        else:
            redirect = self.get_default_redirect()
        return HTTPFound(redirect)

    def cancel_success(self, appstruct):
        """
        handle successfull cancellation of the form
        """
        return self.redirect(appstruct)

    def cancel_failure(self, error):
        appstruct = self.request.POST
        return self.redirect(appstruct)


# class PaymentRemittanceMixin:
#     # def _get_remittance_error(self, error_type, remittance_id, p1="", p2=""):
#     # if error_type == "remittance_closed":
#     #     remittance_route = self.request.route_path(
#     #         "/accounting/bank_remittances/{id}", id=remittance_id
#     #     )
#     #     return ".format(
#     #         remittance_id, remittance_route
#     #     )
#     # if error_type == "payment_mode":
#     #     return "".format(
#     #         remittance_id, p1, p2
#     #     )
#     # if error_type == "payment_bank":
#     #     return .format(
#     #         remittance_id, p1
#     #     )
#     # if error_type == "remittance_unknown":
#     #     return .format(
#     #         remittance_id
#     #     )
#     # if error_type == "old_remittance_closed":
#     #     remittance_route = self.request.route_path(
#     #         "/accounting/bank_remittances/{id}", id=remittance_id
#     #     )
#     #     return "<strong>La remise en banque {0} a été clôturée.</strong>\
#     #     <br/><br/>Il n'est pas possible de modifier le numéro de \
#     #     remise en banque de cet encaissement car la remise a été clôturée.\
#     #     <br/><br/>Vous pouvez remettre l'ancien numéro <strong>{0}\
#     #     </strong> ou rouvrir la remise depuis sa fiche : <a href='#' \
#     #     onclick=\"window.openPopup('{1}');\" title='Voir la remise \
#     #     dans une nouvelle fenêtre' aria-label='Voir la rermise dans \
#     #     une nouvelle fenêtre'>Remise en banque {0}</a>\
#     #     ".format(
#     #         remittance_id, remittance_route
#     #     )
#     # return "Erreur inconnue !"

#     def get_new_remittance_confirm_form(self, appstruct):
#         """
#         Get the payment schema form with a checkbox for
#         remittance creation confirmation
#         """
#         confirm_schema = get_payment_schema(
#             self.request, with_new_remittance_confirm=True
#         )
#         form = self.form_class(confirm_schema, buttons=self.buttons)
#         form.set_appstruct(appstruct)
#         grid = get_form_grid_from_request(self.request)
#         form.widget = GridFormWidget(named_grid=grid)
#         return form.render()

#     def check_payment_remittance(self, appstruct, old_remittance_id=None):
#         """
#         Check the bank remittance id before saving the payment
#         Fills the error_msg attribute if an error was found

#         :returns: A dict with a confirmation form or None
#         :rtype: None or dict
#         """
#         result = None

#         remittance_id = appstruct["bank_remittance_id"]
#         if remittance_id.__contains__("/"):
#             # Remplace les '/' par des '_' et prévient l'utilisateur
#             remittance_id = remittance_id.replace("/", "_")
#             appstruct["bank_remittance_id"] = remittance_id
#             self._warn_message = "Le symbole <strong>/</strong> n'est pas \
#             autorisé dans les numéros de remise en banque. Ce dernier a \
#             été automatiquement modifié en : <strong>{}</strong>\
#             ".format(
#                 remittance_id
#             )

#         if old_remittance_id:
#             br = BankRemittance.query().filter_by(id=old_remittance_id).first()
#             if br.closed:
#                 # Erreur : ancienne remise fermée
#                 self.error_msg = self._get_remittance_error(
#                     "old_remittance_closed", old_remittance_id
#                 )

#         br = BankRemittance.query().filter_by(id=remittance_id).first()
#         if br:
#             if (
#                 br.payment_mode == appstruct["mode"]
#                 and br.bank_id == appstruct["bank_id"]
#             ):  # noqa
#                 if br.closed:
#                     # Erreur : remise déjà fermée
#                     self.error_msg = self._get_remittance_error(
#                         "remittance_closed", remittance_id
#                     )
#             else:
#                 # Erreur : mode de paiement ou banque ne correspondent pas
#                 if br.payment_mode != appstruct["mode"]:
#                     self.error_msg = self._get_remittance_error(
#                         "payment_mode",
#                         remittance_id,
#                         br.payment_mode,
#                         appstruct["mode"],
#                     )
#                 if br.bank_id != appstruct["bank_id"]:
#                     if br.bank:
#                         bank_label = br.bank.label
#                     else:
#                         bank_label = "-NON DEFINI-"
#                     self.error_msg = self._get_remittance_error(
#                         "payment_bank",
#                         remittance_id,
#                         bank_label,
#                     )
#         else:
#             if (
#                 "new_remittance_confirm" in self.request.POST
#                 and self.request.POST["new_remittance_confirm"] == "true"
#             ):  # noqa
#                 # Création de la remise
#                 remittance = BankRemittance(
#                     id=remittance_id,
#                     payment_mode=appstruct["mode"],
#                     bank_id=appstruct["bank_id"],
#                     closed=0,
#                 )
#                 self.request.dbsession.merge(remittance)
#             else:
#                 # Erreur : remise inexistante
#                 self.error_msg = self._get_remittance_error(
#                     "remittance_unknown", remittance_id
#                 )
#                 result = {"form": self.get_new_remittance_confirm_form(appstruct)}

#         return result


class BasePaymentDeleteView(BaseView, PopupMixin):
    def on_after_delete(self):
        """
        Called once the payment has been deleted (optional)
        """
        pass

    def delete_payment(self):
        """
        Delete the payment instance from the database
        """
        raise NotImplementedError

    def parent_url(self, parent_id):
        """
        Parent url to use if a come_from parameter is missing

        :param int parent_id: The id of the parent object
        :returns: The url to redirect to
        :rtype: str
        """
        raise NotImplementedError

    def __call__(self):
        logger.debug("Deleting a payment")
        parent = self.delete_payment()
        self.on_after_delete()

        if self.request.is_popup:
            self.add_popup_response()
            return self.request.response
        # On place le message après pour que la fermeture de popup force le
        # rechargement de la page (sinon la page d'origine contient le message)
        self.session.flash("Le paiement a bien été supprimé")

        if "come_from" in self.request.GET:
            redirect = self.request.GET["come_from"]
        else:
            redirect = self.parent_url(parent.id)
        return HTTPFound(redirect)

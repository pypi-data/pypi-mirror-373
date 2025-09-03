"""
Status change related views

Common to :
    Estimation
    Invoice
    CancelInvoice
    ExpenseSheet
"""
import logging
from urllib.parse import parse_qs, urlparse

import colander
from pyramid.httpexceptions import HTTPFound, HTTPNotFound

from caerp.controllers.state_managers import set_validation_status
from caerp.exception import BadRequest, Forbidden
from caerp.models.services.official_number import LockException
from caerp.utils.html import strip_html_tags
from caerp.utils.rest.apiv1 import RestError
from caerp.utils.strings import format_valid_status_message
from caerp.views import BaseView

logger = logging.getLogger(__name__)


class StatusView(BaseView):
    """
    View for status handling

    See the call method for the workflow and the params
    passed to the methods
    """

    valid_msg = "Le statut a bien été modifié"

    def get_redirect_url(self):
        """
        Return default URL to be redirected after status change
        ----
        To be overriden
        """
        return None

    def redirect(self):
        """
        Redirect function to be used after status processing
        """
        referrer = self.request.referrer
        if referrer and "come_from" in referrer:
            # Redirect to origin if available
            url = parse_qs(urlparse(referrer).query)["come_from"][0]
            if self.context.status == "valid":
                # Display flash message if validation
                validation_message = format_valid_status_message(
                    self.request, self.context
                )
                if validation_message:
                    self.session.flash(validation_message)
        else:
            url = self.get_redirect_url()

        if url:
            if self.request.is_xhr:
                return dict(redirect=url)
            else:
                return HTTPFound(url)
        else:
            return HTTPNotFound()

    def _get_status(self, params):
        """
        Get the status that has been asked for
        """
        return params["submit"]

    def check_allowed(self, status):
        """
        Check that the status change is allowed

        :param str status: The new status that should be affected
        :rtype: bool
        :raises: Forbidden exception if the action isn't allowed
        """
        return True

    def pre_status_process(self, status, params):
        """
        Launch pre process functions
        """

        if hasattr(self, "pre_%s_process" % status):
            func = getattr(self, "pre_%s_process" % status)
            return func(status, params)
        return params

    def status_process(self, status, params):
        """
        Definitively Set the status of the element

        :param str status: The new status that should be affected
        :param dict params: The params that were transmitted by the pre_process
        function
        """
        return set_validation_status(self.request, self.context, status, **params)

    def post_status_process(self, status, params):
        """
        Launch post status process functions

        :param str status: The new status that should be affected
        :param dict params: The params that were transmitted by the associated
        State's callback
        """
        if hasattr(self, "post_%s_process" % status):
            func = getattr(self, "post_%s_process" % status)
            func(status, params)

    def set_status(self, status, params):
        """
        Set the new status to the given item
        handle pre_status and post_status processing

        :param str status: The new status that should be affected
        :param str params: The params retrieved from the request
        """
        pre_params = params

        self.check_allowed(status)
        params = self.pre_status_process(status, pre_params)
        self.status_process(status, params)
        self.post_status_process(status, params)
        return True

    def format_params(self, params: dict):
        """Treat the status related parameters"""
        if "comment" in params:
            params["comment"] = strip_html_tags(params["comment"])
        return params

    def __call__(self):
        """
        Main entry for this view object
        """
        logger.debug("# Entering the status view")
        if self.request.is_xhr:
            params = dict(self.request.json_body)
        else:
            params = dict(self.request.POST)

        if "submit" in params:
            try:
                status = self._get_status(params)
                logger.debug("New status : %s " % status)
                self.set_status(status, params)
                self.context = self.request.dbsession.merge(self.context)
                if not self.request.is_xhr:
                    self.session.flash(self.valid_msg)

                logger.debug(" + The status has been set to {0}".format(status))

            except LockException:
                logger.exception("A lock is not available")
                if self.request.is_xhr:
                    raise RestError(
                        "Une validation est en cours, veuillez attendre quelques "
                        "secondes avant de ré-essayer",
                        code=423,
                    )

            except Forbidden as e:
                logger.exception(
                    " !! Unauthorized action by : {0}".format(
                        self.request.identity.login
                    )
                )
                if self.request.is_xhr:
                    raise RestError(e.message, code=403)
                else:
                    self.session.pop_flash("")
                    self.session.flash(e.message, queue="error")

            except (colander.Invalid, BadRequest) as e:
                logger.exception("Invalid datas")
                if self.request.is_xhr:
                    raise RestError(e.asdict(translate=colander._))
                else:
                    for message in e.messages():
                        self.session.flash(message, "error")

            return self.redirect()

        if self.request.is_xhr:
            raise RestError(
                ["Il manque des arguments pour changer le statut " "du document"]
            )
        else:
            self.session.flash(
                "Il manque des arguments pour changer le statut du document", "error"
            )
            return self.redirect()

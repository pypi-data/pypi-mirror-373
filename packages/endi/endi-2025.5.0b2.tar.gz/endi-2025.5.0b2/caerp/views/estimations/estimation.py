"""
Estimation views


Estimation datas edition :
    date
    address
    customer
    object
    note
    mentions
    ....

Estimation line edition :
    description
    quantity
    cost
    unity
    tva
    ...

Estimation line group edition :
    title
    description

Estimation discount edition

Estimation payment edition

"""

import logging

from pyramid.httpexceptions import HTTPFound

from caerp.consts.permissions import PERMISSIONS
from caerp.controllers.business import gen_sold_invoice
from caerp.controllers.state_managers import get_signed_allowed_actions
from caerp.controllers.task.invoice import attach_invoices_to_estimation
from caerp.forms.tasks.estimation import InvoiceAttachSchema
from caerp.models.company import Company
from caerp.models.task import Estimation, Invoice, PaymentLine
from caerp.resources import estimation_signed_status_js, task_preview_css
from caerp.utils.widgets import Link, ViewLink
from caerp.views import BaseFormView, add_panel_page_view, cancel_btn, submit_btn
from caerp.views.business.business import BusinessOverviewView
from caerp.views.company.routes import (
    COMPANY_ESTIMATION_ADD_ROUTE,
    COMPANY_ESTIMATIONS_ROUTE,
)
from caerp.views.estimations.routes import (
    API_ADD_ROUTE,
    ESTIMATION_ITEM_FILES_ROUTE,
    ESTIMATION_ITEM_GENERAL_ROUTE,
    ESTIMATION_ITEM_PREVIEW_ROUTE,
    ESTIMATION_ITEM_ROUTE,
)
from caerp.views.task.utils import get_task_url
from caerp.views.task.views import (
    TaskAddView,
    TaskDeleteView,
    TaskDuplicateView,
    TaskEditView,
    TaskFilesView,
    TaskFileUploadView,
    TaskGeneralView,
    TaskMoveToPhaseView,
    TaskPdfView,
    TaskPreviewView,
    TaskSetDraftView,
    TaskSetMetadatasView,
)

log = logger = logging.getLogger(__name__)


class EstimationAddView(TaskAddView):
    """
    Estimation add view
    context is a project or company
    """

    factory = Estimation
    title = "Nouveau devis"

    def _after_flush(self, estimation):
        """
        Launch after the new estimation has been flushed
        """
        logger.debug("  + Estimation successfully added : {0}".format(estimation.id))

    def get_api_url(self, _query: dict = {}) -> str:
        return self.request.route_path(
            API_ADD_ROUTE, id=self._get_company_id(), _query=_query
        )

    def get_parent_link(self):
        result = super().get_parent_link()
        if result is not None:
            return result

        referrer = self.request.referrer
        current_url = self.request.current_route_url(_query={})
        if referrer and referrer != current_url and "login" not in referrer:
            if "estimations" in referrer:
                label = "Revenir à la liste des devis"
            elif "dashboard" in referrer:
                label = "Revenir à l'accueil"
            else:
                label = "Revenir en arrière"
            result = Link(referrer, label)
        else:
            result = Link(
                self.request.route_path(COMPANY_ESTIMATIONS_ROUTE, id=self.context.id),
                "Revenir à la liste des devis",
            )
        return result


class EstimationEditView(TaskEditView):
    route_name = ESTIMATION_ITEM_ROUTE

    @property
    def title(self):
        customer = self.context.customer
        customer_label = customer.label
        if customer.code is not None:
            customer_label += " ({0})".format(customer.code)
        return (
            "Modification du {tasktype_label} « {task.name} » avec le client "
            "{customer}".format(
                task=self.context,
                customer=customer_label,
                tasktype_label=self.context.get_type_label().lower(),
            )
        )

    def _before(self):
        """
        Ensure some stuff on the current context
        """
        if not self.context.payment_lines:
            self.context.payment_lines = [
                PaymentLine(description="Solde", amount=self.context.ttc)
            ]
            self.request.dbsession.merge(self.context)
            self.request.dbsession.flush()

    def discount_api_url(self):
        return get_task_url(self.request, suffix="/discount_lines", api=True)

    def post_ttc_api_url(self):
        return get_task_url(self.request, suffix="/post_ttc_lines", api=True)

    def payment_lines_api_url(self):
        return get_task_url(self.request, suffix="/payment_lines", api=True)

    def get_js_app_options(self) -> dict:
        options = super().get_js_app_options()
        options.update(
            {
                "discount_api_url": self.discount_api_url(),
                "post_ttc_api_url": self.post_ttc_api_url(),
                "payment_lines_api_url": self.payment_lines_api_url(),
            }
        )
        return options


class EstimationGeneralView(TaskGeneralView):
    file_route_name = ESTIMATION_ITEM_FILES_ROUTE
    route_name = ESTIMATION_ITEM_GENERAL_ROUTE

    @property
    def title(self):
        return f"Devis {self.context.get_short_internal_number()}"

    def get_actions(self):
        estimation_signed_status_js.need()
        actions = []
        for action in get_signed_allowed_actions(self.request, self.context):
            actions.append(action)
        return actions

    def __call__(self):
        result = super().__call__()
        # On peut récupérer un HTTPFound de la classe parente
        if isinstance(result, dict):
            result["actions"] = self.get_actions()
        return result


class EstimationPreviewView(TaskPreviewView):
    route_name = ESTIMATION_ITEM_PREVIEW_ROUTE

    @property
    def title(self):
        return f"Devis {self.context.get_short_internal_number()}"


class EstimationFilesView(TaskFilesView):
    route_name = ESTIMATION_ITEM_FILES_ROUTE

    @property
    def title(self):
        return f"Devis {self.context.get_short_internal_number()}"


class EstimationPdfView(TaskPdfView):
    pass


class EstimationDuplicateView(TaskDuplicateView):
    label = "le devis"


class EstimationSetMetadatasView(TaskSetMetadatasView):
    @property
    def title(self):
        return "Modification du {tasktype_label} {task.name}".format(
            task=self.context,
            tasktype_label=self.context.get_type_label().lower(),
        )


class EstimationAttachInvoiceView(BaseFormView):
    schema = InvoiceAttachSchema()
    buttons = (
        submit_btn,
        cancel_btn,
    )

    def before(self, form):
        self.request.actionmenu.add(
            ViewLink(
                label="Revenir au devis",
                url=get_task_url(self.request, suffix="/general"),
            )
        )
        form.set_appstruct(
            {"invoice_ids": [str(invoice.id) for invoice in self.context.invoices]}
        )

    @property
    def title(self):
        return f"Factures à rattacher au devis"

    @property
    def title_detail(self):
        return f"({self.context.get_short_internal_number()})"

    def redirect(self):
        return HTTPFound(get_task_url(self.request, suffix="/general"))

    def submit_success(self, appstruct):
        invoice_ids = appstruct.get("invoice_ids")
        invoices = [Invoice.get(invoice_id) for invoice_id in invoice_ids]
        attach_invoices_to_estimation(self.request, self.context, invoices)
        return self.redirect()

    def cancel_success(self, appstruct):
        return self.redirect()

    cancel_failure = cancel_success


def estimation_geninv_view(context, request):
    """
    Invoice generation view : used in shorthanded workflow

    :param obj context: The current context (estimation)
    """
    business = context.business
    invoice = gen_sold_invoice(request, business, ignore_previous_invoices=True)
    context.geninv = True
    request.dbsession.merge(context)

    msg = "Une facture a été générée"
    request.session.flash(msg)
    request.dbsession.flush()
    return HTTPFound(request.route_path("/invoices/{id}", id=invoice.id))


def add_routes(config):
    """
    Add module's specific routes
    """
    for extension in ("pdf", "preview"):
        route = f"{ESTIMATION_ITEM_ROUTE}.{extension}"
        config.add_route(route, route, traverse="/tasks/{id}")

    for action in (
        "addfile",
        "delete",
        "duplicate",
        "geninv",
        "set_metadatas",
        "attach_invoices",
        "set_draft",
        "move",
        "sync_price_study",
    ):
        route = f"{ESTIMATION_ITEM_ROUTE}/{action}"
        config.add_route(route, route, traverse="/tasks/{id}")


class EstimationDeleteView(TaskDeleteView):
    msg = "Le devis {context.name} a bien été supprimée."


def includeme(config):
    add_routes(config)

    config.add_view(
        EstimationAddView,
        route_name=COMPANY_ESTIMATION_ADD_ROUTE,
        renderer="tasks/add.mako",
        permission=PERMISSIONS["context.add_estimation"],
        layout="vue_opa",
        context=Company,
    )
    # Formulaire d'édition d'un devis
    config.add_tree_view(
        EstimationEditView,
        parent=BusinessOverviewView,
        renderer="tasks/form.mako",
        # NB : si le devis n'est pas éditable, c'est la view
        # elle-même qui gère la permission
        permission=PERMISSIONS["company.view"],
        layout="opa",
        context=Estimation,
    )

    config.add_view(
        EstimationDeleteView,
        route_name="/estimations/{id}/delete",
        permission=PERMISSIONS["context.delete_estimation"],
        request_method="POST",
        require_csrf=True,
        context=Estimation,
    )

    config.add_view(
        EstimationDuplicateView,
        route_name="/estimations/{id}/duplicate",
        permission=PERMISSIONS["context.duplicate_estimation"],
        renderer="tasks/duplicate.mako",
        context=Estimation,
    )
    add_panel_page_view(
        config,
        "task_pdf_content",
        js_resources=(task_preview_css,),
        route_name="/estimations/{id}.preview",
        permission=PERMISSIONS["company.view"],
        context=Estimation,
    )

    config.add_view(
        EstimationPdfView,
        route_name="/estimations/{id}.pdf",
        permission=PERMISSIONS["company.view"],
        context=Estimation,
    )

    config.add_view(
        TaskFileUploadView,
        route_name="/estimations/{id}/addfile",
        renderer="base/formpage.mako",
        permission=PERMISSIONS["context.add_file"],
        context=Estimation,
    )

    config.add_view(
        estimation_geninv_view,
        route_name="/estimations/{id}/geninv",
        permission=PERMISSIONS["context.geninv_estimation"],
        request_method="POST",
        require_csrf=True,
        context=Estimation,
    )

    config.add_view(
        EstimationSetMetadatasView,
        route_name="/estimations/{id}/set_metadatas",
        permission=PERMISSIONS["company.view"],
        renderer="tasks/duplicate.mako",
        context=Estimation,
    )
    config.add_view(
        TaskMoveToPhaseView,
        route_name="/estimations/{id}/move",
        permission=PERMISSIONS["company.view"],
        require_csrf=True,
        request_method="POST",
        context=Estimation,
    )
    config.add_view(
        TaskSetDraftView,
        route_name="/estimations/{id}/set_draft",
        permission=PERMISSIONS["context.set_draft_estimation"],
        require_csrf=True,
        request_method="POST",
        context=Estimation,
    )

    config.add_view(
        EstimationAttachInvoiceView,
        route_name="/estimations/{id}/attach_invoices",
        permission=PERMISSIONS["company.view"],
        renderer="/base/formpage.mako",
        context=Estimation,
    )

    config.add_tree_view(
        EstimationGeneralView,
        parent=BusinessOverviewView,
        layout="estimation",
        renderer="tasks/estimation/general.mako",
        permission=PERMISSIONS["company.view"],
        context=Estimation,
    )
    config.add_tree_view(
        EstimationPreviewView,
        parent=BusinessOverviewView,
        layout="estimation",
        renderer="tasks/preview.mako",
        permission=PERMISSIONS["company.view"],
        context=Estimation,
    )
    config.add_tree_view(
        EstimationFilesView,
        parent=BusinessOverviewView,
        layout="estimation",
        renderer="tasks/files.mako",
        permission=PERMISSIONS["company.view"],
        context=Estimation,
    )

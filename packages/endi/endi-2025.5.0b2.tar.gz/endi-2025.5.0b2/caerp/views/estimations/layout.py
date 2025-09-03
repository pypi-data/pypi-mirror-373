from caerp.consts.permissions import PERMISSIONS
from caerp.services.smtp.task import is_node_sent_by_email
from caerp.utils.widgets import POSTButton, Link

from caerp.resources import estimation_signed_status_js

from caerp.views.smtp.routes import SEND_MAIL_ROUTE
from caerp.views.task.utils import get_task_url, task_pdf_link
from caerp.views.task.layout import TaskLayout, get_task_menu
from .routes import (
    ESTIMATION_ITEM_FILES_ROUTE,
    ESTIMATION_ITEM_GENERAL_ROUTE,
    ESTIMATION_ITEM_PREVIEW_ROUTE,
)


def estimation_menu(layout_class):
    menu = get_task_menu(
        ESTIMATION_ITEM_GENERAL_ROUTE,
        ESTIMATION_ITEM_PREVIEW_ROUTE,
        ESTIMATION_ITEM_FILES_ROUTE,
    )
    return menu


class EstimationLayout(TaskLayout):
    menu_factory = estimation_menu

    @property
    def title(self):
        internal = ""
        if self.context.internal:
            internal = "interne "
        return (
            f"Devis {internal}N<span class='screen-reader-text'>umér</span>"
            f"<sup>o</sup>{self.context.get_short_internal_number()} avec le client "
            f"{self.context.customer.label}"
        )

    def stream_main_actions(self):
        has_invoices = len(self.context.invoices) > 0

        if self.context.business.visible:
            yield Link(
                self.request.route_path(
                    "/businesses/{id}", id=self.context.business_id
                ),
                label="Voir l'affaire",
                title="Voir l’affaire : {}".format(self.context.business.name),
                icon="folder",
            )
        else:
            params = {
                "url": get_task_url(self.request, suffix="/geninv"),
                "label": "Facturer",
                "icon": "file-invoice-euro",
                "title": "Transformer ce devis en facture",
                "css": "btn icon btn-primary",
            }
            if has_invoices or self.context.geninv:
                params["label"] = "Re-facturer"
                params["title"] = "Transformer à nouveau ce devis en facture"
                params["icon"] = "file-redo"

            yield POSTButton(**params)

        if self.request.has_permission(PERMISSIONS["context.set_draft_estimation"]):
            yield POSTButton(
                get_task_url(self.request, suffix="/set_draft"),
                label="Repasser en brouillon",
                icon="pen",
                css="btn btn-primary icon_only_mobile",
                title="Repasser ce devis en brouillon pour pouvoir le modifier",
            )

        if not has_invoices and not self.context.internal:
            yield Link(
                get_task_url(self.request, suffix="/attach_invoices"),
                'Rattacher<span class="no_tablet">&nbsp;à des factures</span>',
                title="Rattacher ce devis à des factures",
                icon="link",
                css="btn icon_only_mobile",
            )

        if self.request.has_permission(
            PERMISSIONS["context.gen_supplier_order_estimation"]
        ):
            yield POSTButton(
                get_task_url(self.request, suffix="/gen_supplier_order"),
                "Commande fournisseur",
                icon="plus",
                title=(
                    "Générer la commande fournisseur dans l'espace de "
                    "l'enseigne {}".format(self.context.customer.label)
                ),
            )

        if (
            self.context.status == "valid"
            and self.context.company.smtp_configuration != "none"
        ):
            confirm = None
            if is_node_sent_by_email(self.request, self.context):
                confirm = (
                    "Ce devis a déjà été envoyé, souhaitez-vous l’envoyer de nouveau ?"
                )
            yield Link(
                self.request.route_path(SEND_MAIL_ROUTE, id=self.context.id),
                label="Envoyer au client",
                title="Envoyer ce devis par email au client",
                icon="envelope",
                css="btn icon_only_mobile",
                confirm=confirm,
            )

    def stream_more_actions(self):
        if (
            self.context.business.business_type.bpf_related
            and self.request.has_permission(
                PERMISSIONS["context.edit_bpf"], self.context.business
            )
        ):
            yield Link(
                self.request.route_path(
                    "/businesses/{id}/bpf", id=self.context.business_id
                ),
                label="BPF",
                title="Voir les données BPF de l'affaire",
                icon="chart-pie",
            )
        if self.request.has_permission(PERMISSIONS["context.duplicate_estimation"]):
            yield Link(
                get_task_url(self.request, suffix="/duplicate"),
                label="",
                title="Dupliquer ce devis",
                icon="copy",
            )
        yield Link(
            get_task_url(self.request, suffix="/set_metadatas"),
            "",
            title="Déplacer ou renommer ce devis",
            icon="folder-move",
        )
        yield task_pdf_link(self.request, "ce devis")


def includeme(config):
    config.add_layout(
        EstimationLayout,
        template="caerp:templates/tasks/estimation/layout.mako",
        name="estimation",
    )

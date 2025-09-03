from caerp.consts.permissions import PERMISSIONS
from pyramid.httpexceptions import HTTPFound

from caerp_celery.mail import (
    send_customer_new_order_mail,
    send_supplier_new_order_mail,
    send_customer_new_invoice_mail,
    send_supplier_new_invoice_mail,
)
from caerp.models.task import (
    InternalInvoice,
    InternalEstimation,
    InternalCancelInvoice,
)
from caerp.views.supply.utils import get_supplier_doc_url


def generate_order_from_estimation_view(context, request):
    """
    View launching the generation of the internal supplier order from an
    internal estimation
    """
    if request.has_permission(PERMISSIONS["context.gen_supplier_order_estimation"]):
        # Hack pour gérer la latence de la génération de la commande fournisseur
        # Le bouton d'ajout de commande fournisseur apparaît alors qu'elle est
        # en cours de création/déjà créée
        order = context.sync_with_customer(request)
        send_customer_new_order_mail(request, order)
        send_supplier_new_order_mail(request, order)
    else:
        order = context.supplier_order

    msg = "Une commande fournisseur a été générée dans l'espace enDI de " "{}".format(
        context.customer.label
    )
    if request.has_permission(PERMISSIONS["company.view"], order):
        url = get_supplier_doc_url(request, doc=order)
        msg += " <a href='{}' title='Voir la commande fournisseur'>Voir" "</a>".format(
            url
        )
    request.session.flash(msg)

    if request.referer:
        redirect = request.referer
    else:
        redirect = request.route_path("/estimations/{id}", id=context.id)
    return HTTPFound(redirect)


def generate_supplier_invoice_from_invoice_view(context, request):
    """
    View launching the generation of the internal supplier invoice from an
    internal invoice or an internal cancelinvoice
    """
    if request.has_permission(PERMISSIONS["context.gen_supplier_invoice_invoice"]):
        # Hack pour gérer la latence de la génération de la facture fournisseur
        # Le bouton d'ajout de facture fournisseur apparaît alors qu'elle est
        # en cours de création/déjà créée
        supplier_invoice = context.sync_with_customer(request)
        send_customer_new_invoice_mail(request, supplier_invoice)
        send_supplier_new_invoice_mail(request, supplier_invoice)
    else:
        supplier_invoice = context.supplier_invoice

    msg = "Une facture fournisseur a été générée dans l'espace enDI de " "{}".format(
        context.customer.label
    )
    if request.has_permission(PERMISSIONS["company.view"], supplier_invoice):
        url = request.route_path("/supplier_invoices/{id}", id=supplier_invoice.id)
        msg += " <a href='{}' title='Voir la facture fournisseur'>Voir" "</a>".format(
            url
        )
    request.session.flash(msg)
    if request.referer:
        redirect = request.referer
    else:
        redirect = request.route_path("/invoices/{id}", id=context.id)
    return HTTPFound(redirect)


def includeme(config):
    config.add_view(
        generate_order_from_estimation_view,
        route_name="/estimations/{id}/gen_supplier_order",
        permission=PERMISSIONS["company.view"],
        context=InternalEstimation,
        request_method="POST",
    )
    config.add_view(
        generate_supplier_invoice_from_invoice_view,
        route_name="/invoices/{id}/gen_supplier_invoice",
        permission=PERMISSIONS["company.view"],
        context=InternalInvoice,
        request_method="POST",
    )
    config.add_view(
        generate_supplier_invoice_from_invoice_view,
        route_name="/cancelinvoices/{id}/gen_supplier_invoice",
        permission=PERMISSIONS["company.view"],
        context=InternalCancelInvoice,
        request_method="POST",
    )

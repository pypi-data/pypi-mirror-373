import os

from caerp.consts.permissions import PERMISSIONS
from caerp.views.admin.tools import BaseAdminIndexView
from caerp.views.admin.supplier import (
    SUPPLIER_URL,
    SupplierIndexView,
)

SUPPLIER_ACCOUNTING_URL = os.path.join(SUPPLIER_URL, "accounting")

SUPPLIER_INFO_MESSAGE = """Configurez les exports comptables des factures \
et paiements fournisseur.<br/>
<h4>Variables utilisables dans les gabarits de libellés</h4>\
<p>Il est possible de personaliser les libellés comptables à l'aide d'un \
gabarit. Plusieurs variables sont disponibles :</p>\
<ul>\
    <li><code>{company.name}</code> : le nom de l'enseigne concernée</li>\
    <li><code>{company.code_compta}</code> : le code analytique de l'enseigne concernée</li>\
    <li><code>{supplier.label}</code> : le nom du fournisseur concerné</li>\
    <li><code>{supplier_invoice.official_number}</code> : le numéro de\
    la facture fournisseur enDI</li>\
    <li><code>{supplier_invoice.remote_invoice_number}</code> : le numéro de\
    facture du fournisseur, tel que mentionné sur le document fournisseur</li>\
    <li><code>{line_description}</code> : la description de la ligne de la\
    facture fournisseur (<strong>seulement pour les factures fournisseur, et si\
    l'export est dégroupé</strong>)</li>\
    <li><code>{beneficiaire_LASTNAME}</code> : le nom de l'entrepreneur concerné\
    (<strong>seulement pour les remboursements et abandons de créance</strong>)</li>\
</ul>"""


class SupplierAccountingIndex(BaseAdminIndexView):
    title = "Configuration comptable du module Fournisseur"
    description = "Configurer la génération des écritures fournisseur"
    route_name = SUPPLIER_ACCOUNTING_URL
    permission = PERMISSIONS["global.config_accounting"]


def includeme(config):
    config.add_route(SUPPLIER_ACCOUNTING_URL, SUPPLIER_ACCOUNTING_URL)
    config.add_admin_view(
        SupplierAccountingIndex,
        parent=SupplierIndexView,
    )
    config.include(".supplier_invoice")
    config.include(".internalsupplier_invoice")

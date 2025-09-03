import os

from caerp.consts.permissions import PERMISSIONS
from caerp.forms.admin import get_config_schema
from caerp.views.admin.tools import (
    BaseConfigView,
    BaseAdminIndexView,
)
from caerp.views.admin.supplier import (
    SUPPLIER_URL,
    SupplierIndexView,
)


SUPPLIER_NUMBERING_CONFIG_URL = os.path.join(SUPPLIER_URL, "numbering")
INVOICE_NUMBERING_CONFIG_URL = os.path.join(
    SUPPLIER_NUMBERING_CONFIG_URL, "supplier_invoice"
)


class SupplierNumberingIndex(BaseAdminIndexView):
    title = "Comptabilité : Numérotation des factures fournisseurs"
    description = (
        "Configurer la numérotation des différents type de facture " "fournisseur"
    )
    route_name = SUPPLIER_NUMBERING_CONFIG_URL


class SupplierInvoiceNumberingConfigView(BaseConfigView):
    title = "Factures fournisseurs"
    description = "Configurer la manière dont sont numérotées les Factures fournisseurs"

    route_name = INVOICE_NUMBERING_CONFIG_URL

    keys = (
        "supplierinvoice_number_template",
        "global_supplierinvoice_sequence_init_value",
        "year_supplierinvoice_sequence_init_value",
        "year_supplierinvoice_sequence_init_date",
        "month_supplierinvoice_sequence_init_value",
        "month_supplierinvoice_sequence_init_date",
    )

    schema = get_config_schema(keys)

    info_message = """Il est possible de personaliser le gabarit du numéro \
de facture fournisseur.<br/ >\
<p>Plusieurs variables et séquences chronologiques sont à disposition.</p>\
<h4>Variables :</h4>\
<ul>\
<li><code>{YYYY}</code> : année, sur 4 digits</li>\
<li><code>{YY}</code> : année, sur 2 digits</li>\
<li><code>{MM}</code> : mois, sur 2 digits</li>\
<li><code>{ANA}</code> : code analytique de l'enseigne</li>\
</ul>\
<h4>Numéros de séquence :</h4>\
<ul>\
<li><code>{SEQGLOBAL}</code> : numéro de séquence global (aucun ràz)</li>\
<li><code>{SEQYEAR}</code> : numéro de séquence annuel (ràz chaque année)\
</li>
<li><code>{SEQMONTH}</code> : numéro de séquence mensuel (ràz chaque mois)\
</li>\
<li><code>{SEQMONTHANA}</code>: numéro de séquence par enseigne et par moisi\
(ràz chaque mois)</li>\
</ul>\
<br/ >\
<p>Dans le cas d'une migration depuis un autre outil de gestion, il est possible \
d'initialiser les séquences à une valeur différente de zéro.</p>\
<p>La valeur définie ici correspond à la dernière déjà utilisée, \
la numérotation reprendra au numéro suivant.</p>\
    """


def add_routes(config):
    config.add_route(
        SUPPLIER_NUMBERING_CONFIG_URL,
        SUPPLIER_NUMBERING_CONFIG_URL,
    )
    config.add_route(
        INVOICE_NUMBERING_CONFIG_URL,
        INVOICE_NUMBERING_CONFIG_URL,
    )


def includeme(config):
    add_routes(config)
    config.add_admin_view(
        SupplierNumberingIndex,
        parent=SupplierIndexView,
        permission=PERMISSIONS["global.config_supply"],
    )
    config.add_admin_view(
        SupplierInvoiceNumberingConfigView,
        parent=SupplierNumberingIndex,
        permission=PERMISSIONS["global.config_supply"],
    )

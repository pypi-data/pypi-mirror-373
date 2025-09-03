"""
Admin view for accounting software related settings
"""

import logging
import os

from caerp.consts.permissions import PERMISSIONS
from caerp.forms.admin import get_config_schema
from caerp.views.admin.sale.accounting.numbers import SALE_NUMBERING_CONFIG_URL
from caerp.views.admin.sale.accounting.invoice import (
    CONFIG_URL as INVOICE_CONFIG_URL,
    ModuleListView,
)
from caerp.views.admin.sale.accounting.receipts import RECEIPT_CONFIG_URL
from caerp.views.admin.expense.accounting import (
    EXPENSE_ACCOUNTING_URL,
    EXPENSE_PAYMENT_ACCOUNTING_URL,
)
from caerp.views.admin.supplier.accounting import (
    SUPPLIER_ACCOUNTING_URL,
)
from caerp.views.admin.accounting import (
    AccountingIndexView,
    ACCOUNTING_URL,
)
from caerp.views.admin.tools import BaseConfigView


logger = logging.getLogger(__name__)


BASE_URL = os.path.join(ACCOUNTING_URL, "accounting_software")


class AccountingSoftwareView(BaseConfigView):
    title = "Logiciel de comptabilité"
    description = "Configurer les informations concernant le logiciel de comptabilité."
    route_name = BASE_URL

    validation_msg = "Les informations ont bien été enregistrées"
    keys = ("accounting_software", "accounting_label_maxlength")
    schema = get_config_schema(keys)
    permission = PERMISSIONS["global.config_accounting"]

    @property
    def info_message(self):
        return """D'autres paramètres liés au logiciel de comptabilité sont \
disponibles :
<ul>
    <li>Les numéros de facture dans <a href={}>Module ventes → \
Numérotation des factures</a></li>\
    <li>Les différents libellés d'écritures comptables :\
    <ul>\
      <li><a href="{}">Module Notes de dépenses → \
Export comptable des notes de dépenses</a></li>\
      <li><a href="{}">Module Notes de dépenses →  \
Export comptable des décaissements </a></li>\
      <li><a href="{}">Module Ventes → Configuration comptable du \
module de vente →  Informations générales et modules \
prédéfinis</a></li>\
      <li><a href="{}">Module Ventes → Configuration comptable du module \
de vente → Modules de contribution personnalisés</a></li>\
      <li><a href="{}">Module Ventes → Configuration comptable des \
encaissements → Informations générales</a></li>\
      <li><a href="{}">Module Fournisseurs → Configuration comptable du \
module Fournisseur</a></li>\
    </ul>\
    </li>\
</ul>\
""".format(
            *[
                self.request.route_path(i)
                for i in [
                    SALE_NUMBERING_CONFIG_URL,
                    EXPENSE_ACCOUNTING_URL,
                    EXPENSE_PAYMENT_ACCOUNTING_URL,
                    INVOICE_CONFIG_URL,
                    ModuleListView.route_name,
                    RECEIPT_CONFIG_URL,
                    SUPPLIER_ACCOUNTING_URL,
                ]
            ]
        )


def includeme(config):
    config.add_route(BASE_URL, BASE_URL)
    config.add_admin_view(
        AccountingSoftwareView,
        parent=AccountingIndexView,
    )

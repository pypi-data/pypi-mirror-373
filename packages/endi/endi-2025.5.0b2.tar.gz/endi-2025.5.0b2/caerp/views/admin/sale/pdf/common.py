import os
from caerp.consts.permissions import PERMISSIONS
from caerp.forms.admin import get_config_schema
from caerp.views.admin.tools import BaseConfigView
from caerp.views.admin.main.cae import MAIN_CAE_ROUTE
from caerp.views.admin.sale.pdf import (
    PdfIndexView,
    PDF_URL,
)

COMMON_ROUTE = os.path.join(PDF_URL, "common")


class CommonConfigView(BaseConfigView):
    title = "Informations communes aux devis et factures"
    description = "Configurer les Conditions générales de vente, les pieds de \
page des sorties PDF"
    info_message = (
        """
    Il est possible de configurer le nom des fichiers pdf des documents 
    (devis/factures/avoirs).
    .<br/ >\
<p>Plusieurs variables et séquences chronologiques sont à disposition.</p>\
<h4>Variables :</h4>\
<ul>\
<li><code>{type_document}</code> : Type de document (facture/devis/avoir)</li>\
<li><code>{numero}</code> : Numéro du document</li>\
<li><code>{enseigne}</code> : Nom de l'enseigne</li>\
<li><code>{client}</code> : Nom du client</li>\
<li><code>{cae}</code> : Nom de la CAE tel que configuré <a href="%s" aria-label="Ouvrir la page de configuration du nom de la CAE dans une nouvelle fenêtre" target="_blank">Ici</a></li>\
</ul>\
    """
        % MAIN_CAE_ROUTE
    )
    keys = [
        "sale_pdf_filename_template",
        "coop_cgv",
        "coop_pdffootertitle",
        "coop_pdffootertext",
        "coop_pdffootercourse",
    ]
    schema = get_config_schema(keys)
    validation_msg = "Vos modifications ont été enregistrées"
    route_name = COMMON_ROUTE
    permission = PERMISSIONS["global.config_sale"]


def includeme(config):
    config.add_route(COMMON_ROUTE, COMMON_ROUTE)
    config.add_admin_view(
        CommonConfigView,
        parent=PdfIndexView,
    )

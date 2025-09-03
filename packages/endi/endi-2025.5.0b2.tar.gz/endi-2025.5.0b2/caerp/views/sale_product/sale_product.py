import logging
from caerp.consts.permissions import PERMISSIONS
from typing import Dict

from caerp.forms.sale_product.json_import import JSONSalesCatalogImportSchema
from caerp.models.company import Company
from caerp.views.csv_import import get_current_uploaded_filepath
from caerp.views.sale_product.routes import (
    PRODUCT_API_ROUTE,
    CATALOG_ROUTE,
    CATALOG_API_ROUTE,
    CATEGORY_API_ROUTE,
)

from caerp.resources import sale_product_resources
from caerp.views import (
    AsyncJobMixin,
    BaseFormView,
    BaseView,
    JsAppViewMixin,
)
from caerp_celery.models import (
    CsvImportJob,
    FileGenerationJob,
)
from caerp_celery.tasks.export import export_company_sales_catalog_to_json
from caerp_celery.tasks.json_import import import_json_company_sales_catalog

logger = logging.getLogger(__name__)


class SaleProductView(BaseView, JsAppViewMixin):
    title = "Catalogue des produits"

    def context_url(self, _query: Dict[str, str] = {}):
        return self.request.route_path(
            PRODUCT_API_ROUTE, id=self.context.id, _query=_query
        )

    def category_url(self):
        return self.request.route_path(
            CATEGORY_API_ROUTE,
            id=self.context.id,
        )

    def catalog_tree_url(self):
        return self.request.route_path(
            CATALOG_API_ROUTE,
            id=self.context.id,
        )

    def more_js_app_options(self):
        return dict(
            catalog_tree_url=self.catalog_tree_url(),
            category_url=self.category_url(),
        )

    def __call__(self):
        sale_product_resources.need()
        return dict(title=self.title, urls=self.get_js_app_options())


class CompanySalesCatalogJSONExportView(
    AsyncJobMixin,
    BaseView,
):
    """
    View dedicated to the catalog Celery export job

    Runs, watches and download the file when ready
    Intended to be run in a popup.
    """

    def __call__(self):
        company_id = self.request.context.id

        celery_error_resp = self.is_celery_alive()
        if celery_error_resp:
            return celery_error_resp

        job_result = self.initialize_job_result(FileGenerationJob, force_download=True)
        celery_job = export_company_sales_catalog_to_json.delay(
            job_result.id, company_id
        )
        return self.redirect_to_job_watch(celery_job, job_result)


class CompanyJSONSalesCatalogImportview(AsyncJobMixin, BaseFormView):
    """
    Upload a file for import, validate its structure, and pass it to celery task
    """

    title = "Import de catalogue produits"
    help_message = """
    <p>
    Ce formulaire permet d'importer un catalogue produit préalablement 
    exporté avec enDI (du même serveur ou d'un serveur différent) au format JSON.
    </p>
    <br />
    <p>Les données sont importées selon les règles suivantes :</p>
    <ul>
        <li>Les produits sont recréés à l'identique, y compris les produits composés</li>
        <li>Aucune détection de doublon n'est faite pour les produits</li>
        <li>Les catégories de produits sont créées à la volée si nécessaire</li>
        <li>Les comptes produits, taux de TVA et unités sont rattachées si elles existent (même code comptable + même TVA), laissés vides sinon</li>
        <li>Les fournisseur sont rattachés si ils existent (même nom), laissés vides sinon</li>
        <li>Le stock est transféré</li>
    </ul>
    <br />
    <p>
        Les cas suivants Donneront lieu à un avertissement car un champ présent dans l'import sera laissé vide faute de correspondance trouvée dans le catalogue.
    </p>
    """

    schema = JSONSalesCatalogImportSchema()
    add_template_vars = ("title", "help_message")

    def submit_success(self, appstruct):
        logger.debug("A csv file has been uploaded")
        file_uid = appstruct["csv_file"]["uid"]

        company_id = self.request.context.id

        celery_error_resp = self.is_celery_alive()
        if celery_error_resp:
            return celery_error_resp

        job_result = self.initialize_job_result(CsvImportJob)

        filepath = get_current_uploaded_filepath(
            self.request, appstruct["csv_file"]["uid"]
        )

        celery_job = import_json_company_sales_catalog.delay(
            job_result.id,
            company_id,
            filepath,
        )
        return self.redirect_to_job_watch(celery_job, job_result)


def includeme(config):
    config.add_view(
        CompanySalesCatalogJSONExportView,
        route_name=CATALOG_ROUTE,
        request_param="action=export_json",
        # kind-a artificial, just to take precedence over the next route (more specific)
        request_method="GET",
        context=Company,
        permission=PERMISSIONS["company.view"],
    )
    config.add_view(
        CompanyJSONSalesCatalogImportview,
        route_name=CATALOG_ROUTE,
        request_param="action=import_json",
        # kind-a artificial, just to take precedence over the next route (more specific)
        request_method=["GET", "POST"],
        renderer="base/formpage.mako",
        context=Company,
        permission=PERMISSIONS["context.add_sale_product"],
    )
    config.add_view(
        CompanyJSONSalesCatalogImportview,
        route_name=CATALOG_ROUTE,
        request_param="action=import_json",
        # kind-a artificial, just to take precedence over the next route (more specific)
        request_method=["POST"],
        context=Company,
        permission=PERMISSIONS["context.add_sale_product"],
    )
    config.add_view(
        SaleProductView,
        route_name=CATALOG_ROUTE,
        renderer="/sale/products.mako",
        layout="opa",
        context=Company,
        permission=PERMISSIONS["company.view"],
    )
    config.add_company_menu(
        parent="sale",
        order=0,
        label="Catalogue produits",
        route_name=CATALOG_ROUTE,
        route_id_key="company_id",
        routes_prefixes=[
            "sale_categories",
            "sale_category",
            "sale_products_group",
            "sale_product_groups",
            "sale_training_group",
            "sale_training_groups",
        ],
    )

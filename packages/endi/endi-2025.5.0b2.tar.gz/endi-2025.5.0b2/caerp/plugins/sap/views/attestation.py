import logging

import colander
from sqlalchemy.orm import load_only
from caerp_celery.models import (
    FileGenerationJob,
    BulkFileGenerationJob,
)

from caerp.consts.permissions import PERMISSIONS
from caerp.models.company import Company
from caerp.models.files import File
from caerp.utils.files import get_timestamped_filename

from ..models.sap import (
    SAPAttestation,
    SAPAttestationLine,
)
from caerp.models.third_party.customer import Customer
from caerp.utils.widgets import Link
from caerp.views import (
    AsyncJobMixin,
    BaseFormView,
    BaseListView,
    TreeMixin,
    BaseView,
)

from ..forms.attestation import (
    AttestationGenerateSchema,
    get_list_schema,
)
from ..celery_jobs import (
    merge_pdf_files,
    generate_attestations,
)
from ..models.services.attestation import (
    SAPAttestationLineService,
)

logger = logging.getLogger(__name__)

VIEW_HELP_TEXT = """
enDi gère une unique attestation par client, par enseigne et par an. Si de
nouvelles prestations ou de nouveaux paiements se sont ajoutées depuis la
génération, il est possible de regénérer l'attestation.
"""


class SAPListTools:
    route_name = "/sap/attestations"
    schema = get_list_schema()

    sort_columns = {
        "name": "name",
        "year": "year",
        "company": Company.name,
        "customer": Customer.name,
        "amount": "amount",
        "updated_at": "updated_at",
    }

    def query(self):
        query = SAPAttestation.query().join(SAPAttestation.customer)
        query = query.join(Customer.company)
        return query

    def filter_year(self, query, appstruct):
        year = appstruct.get("year", -1)
        if year and year not in (-1, colander.null):
            query = query.filter(SAPAttestation.year == year)
        return query

    def filter_company(self, query, appstruct):
        company_id = appstruct.get("company_id")
        if company_id:
            query = query.filter(Customer.company_id == company_id)
        return query

    def filter_customer(self, query, appstruct):
        customer_id = appstruct.get("customer_id")
        if customer_id:
            query = query.filter(SAPAttestation.customer_id == customer_id)
        return query

    def filter_search(self, query, appstruct):
        search = appstruct.get("search")
        if search:
            query = query.filter(Customer.name.like("%" + search + "%"))
        return query


class GlobalSapAttestationListView(SAPListTools, TreeMixin, BaseListView):
    title = "Liste des attestations fiscales annuelles SAP"
    add_template_vars = [
        "help_message",
        "stream_actions",
        "pdf_url",
        "bulk_pdf_export_url",
    ]
    help_message = VIEW_HELP_TEXT

    @property
    def bulk_pdf_export_url(self):
        querystring = dict()
        # copy the filters from filtered list view
        querystring.update(self.request.params)
        querystring["action"] = "export_pdf"
        return self.request.route_path("/sap/attestations", _query=querystring)

    def pdf_url(self, attestation):
        if attestation.files:
            return self.request.route_path(
                "/files/{id}",
                id=attestation.files[0].id,
                _query=dict(action="download"),
            )
        else:
            return None

    def stream_actions(self, attestation):
        yield Link(
            self.pdf_url(attestation),
            "PDF",
            title="Télécharger le PDF de l'attestation",
            icon="file-pdf",
        )
        # Uncomment for tests
        # yield Link(
        #     self.request.route_path(
        #         "/sap/attestations/{year}/{customer_id}.preview",
        #         year=attestation.year,
        #         customer_id=attestation.customer_id,
        #     ),
        #     "PDF preview",
        #     title="Prévisualisation (dév)",
        #     icon='eye',
        # )


class GlobalSapAttestationBulkPdfView(
    AsyncJobMixin,
    SAPListTools,
    BaseListView,
):
    @property
    def exported_filename(self):
        return get_timestamped_filename("export_sap_attestations", "pdf")

    def query(self):
        # Only load ids
        query = super().query()
        return query.options(load_only(SAPAttestation.id))

    def _build_return_value(self, schema, appstruct, query):
        all_ids = [elem.id for elem in query]
        file_ids = [
            a[0]
            for a in self.dbsession.query(File.id).filter(File.parent_id.in_(all_ids))
        ]
        if not file_ids:
            return self.show_error(
                "Aucune attestation ne correspond à ces critères,"
                " peut-être devriez-vous les générer avant ?"
            )
        else:
            celery_error_resp = self.is_celery_alive()
            if celery_error_resp:
                return celery_error_resp
            else:
                job_result = self.initialize_job_result(FileGenerationJob)
                job = merge_pdf_files.delay(
                    job_result.id,
                    file_ids,
                    self.exported_filename,
                )
                return self.redirect_to_job_watch(job, job_result)


class GenerateSapAttestationView(
    TreeMixin,
    BaseFormView,
    AsyncJobMixin,
):
    title = "Générer des attestations"
    route_name = "/sap/attestations/generate"

    schema = AttestationGenerateSchema()
    add_template_vars = ["help_message"]

    help_message = VIEW_HELP_TEXT

    redirect_route = "/sap/attestations"

    def before(self, form):
        self.populate_navigation()

    def submit_success(self, appstruct):
        regenerate_existing = appstruct.get("regenerate_existing", False)

        companies_ids = appstruct.get("companies_ids", set())
        customers_ids = appstruct.get("customers_ids", set())
        year = appstruct["year"]

        celery_error_resp = self.is_celery_alive()
        if celery_error_resp:
            return celery_error_resp

        job_result = self.initialize_job_result(BulkFileGenerationJob)
        celery_job = generate_attestations.delay(
            job_result.id,
            list(companies_ids),
            list(customers_ids),
            regenerate_existing,
            year,
        )
        return self.redirect_to_job_watch(celery_job, job_result)


class SAPAttestationPreview(BaseView):
    """
    Return the html structure used in pdf generation
    """

    def __call__(self):
        from caerp.resources import pdf_css

        pdf_css.need()
        customer_id = int(self.request.matchdict["customer_id"])
        year = int(self.request.matchdict["year"])

        lines = SAPAttestationLineService().query(
            year=year,
            companies_ids=set(),
            customers_ids={customer_id},
        )
        lines = list(lines)
        SAPAttestationLine.sort_for_grouping(lines)
        attestation = (
            SAPAttestation.query()
            .filter_by(
                customer_id=customer_id,
                year=year,
            )
            .first()
        )
        return dict(
            lines=lines,
            attestation=attestation,
        )


def add_routes(config):
    config.add_route(
        "/sap/attestations/generate",
        "/sap/attestations/generate",
    )
    config.add_route(
        "/sap/attestations/{year}/{customer_id}.preview",
        "/sap/attestations/{year}/{customer_id}.preview",
    )
    config.add_route(
        "/sap/attestations",
        "/sap/attestations",
    )


def includeme(config):
    add_routes(config)
    config.add_tree_view(
        GlobalSapAttestationListView,
        renderer="caerp.plugins.sap:/templates/sap/attestations.mako",
        permission=PERMISSIONS["global.view_sap"],
    )

    config.add_view(
        GlobalSapAttestationBulkPdfView,
        route_name="/sap/attestations",
        request_param="action=export_pdf",
        permission=PERMISSIONS["global.view_sap"],
    )

    config.add_tree_view(
        GenerateSapAttestationView,
        parent=GlobalSapAttestationListView,
        renderer="/base/formpage.mako",
        permission=PERMISSIONS["global.view_sap"],
    )

    config.add_view(
        SAPAttestationPreview,
        route_name="/sap/attestations/{year}/{customer_id}.preview",
        permission=PERMISSIONS["global.view_sap"],
        renderer="caerp.plugins.sap:/templates/panels/sap/content_wrapper.mako",
    )

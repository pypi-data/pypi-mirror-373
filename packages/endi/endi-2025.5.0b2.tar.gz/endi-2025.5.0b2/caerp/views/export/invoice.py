"""
Invoice related exports views
"""

import logging

from caerp.consts.permissions import PERMISSIONS
from collections import OrderedDict
from sqlalchemy import or_
from sqlalchemy.orm.exc import MultipleResultsFound

from caerp.export.task_pdf import ensure_task_pdf_persisted
from caerp.interfaces import (
    ITreasuryGroupper,
    ITreasuryProducer,
    ITreasuryInvoiceWriter,
)
from caerp.models.export.accounting_export_log import (
    InvoiceAccountingExportLogEntry,
)
from caerp.models.task import (
    Task,
    Invoice,
    CancelInvoice,
    InternalInvoice,
    InternalCancelInvoice,
)
from caerp.utils.accounting import (
    check_customer_accounting_configuration,
    check_company_accounting_configuration,
)
from caerp.utils.files import get_timestamped_filename
from caerp.utils.widgets import ViewLink
from caerp.views.admin.sale.accounting import (
    ACCOUNTING_INDEX_URL,
)
from caerp.views.admin.sale.accounting.invoice import (
    CONFIG_URL as INVOICE_CONFIG_URL,
)
from caerp.views.admin.sale.accounting.internalinvoice import (
    CONFIG_URL as INTERNALINVOICE_CONFIG_URL,
)
from caerp.views.third_party.customer.routes import CUSTOMER_ITEM_ROUTE
from caerp.views.admin.sale.accounting.tva import TVA_URL
from caerp.views.company.tools import get_company_url
from caerp.views.export import (
    BaseExportView,
)
from caerp.views.export.utils import (
    query_invoices_for_export,
    get_invoice_period_form,
    get_invoice_all_form,
    get_invoice_number_form,
    ACCOUNTING_EXPORT_TYPE_INVOICES,
)
from caerp.views.invoices.routes import INVOICE_COLLECTION_ROUTE
from caerp.views.task.utils import (
    get_task_view_type,
    get_task_url,
)


logger = logging.getLogger(__name__)


MISSING_PRODUCT_ERROR_MSG = """Le document
 <a target="_blank" href="{2}" title="Ce document s’ouvrira dans une nouvelle fenêtre" aria-label="Ce document s’ouvrira dans une nouvelle fenêtre">{0}</a> n'est pas exportable :
des comptes produits sont manquants.
<a onclick="window.openPopup('{1}');" href='#' title="Voir le document dans une nouvelle fenêtre" aria-label="Voir le document s’ouvrira dans une nouvelle fenêtre">Voir le document</a>"""

COMPANY_ERROR_MSG = """Le document
 <a target="_blank" href="{3}" title="Ce document s’ouvrira dans une nouvelle fenêtre" aria-label="Ce document s’ouvrira dans une nouvelle fenêtre">{0}</a> n'est pas exportable :
le code analytique de l'enseigne {1} n'a pas été configuré.
<a onclick="window.openPopup('{2}');" href='#' title="Voir l’enseigne dans une nouvelle fenêtre" aria-label="Voir l’enseigne dans une nouvelle fenêtre">Voir l’enseigne</a>"""

CUSTOMER_ERROR_MSG = """Le document
 <a target="_blank" href="{invoice_url}" title="Ce document s’ouvrira dans une nouvelle fenêtre" aria-label="Ce document s’ouvrira dans une nouvelle fenêtre"> {official_number}</a> n'est pas exportable :
impossible de déterminer le compte général client à utiliser.

Il peut être configuré à différents niveaux :
<a onclick="window.openPopup('{customer_url}');" href='#' title="Voir le client dans une nouvelle fenêtre" aria-label="Voir le client dans une nouvelle fenêtre">
Client {customer_label}</a> /
<a onclick="window.openPopup('{company_url}');" href='#' title="Voir l’enseigne dans une nouvelle fenêtre" aria-label="Voir l’enseigne dans une nouvelle fenêtre">
Enseigne {company_label}</a> /
<a onclick="window.openPopup('{admin_url}');" href='#' title="Voir la CAE dans une nouvelle fenêtre" aria-label="Voir la CAE dans une nouvelle fenêtre">
CAE</a> /
<a onclick="window.openPopup('{admin_tva_url}');" href='#' title="Voir les TVAs dans une nouvelle fenêtre" aria-label="Voir les TVAs dans une nouvelle fenêtre">
TVA</a>.
"""

MISSING_RRR_CONFIG_ERROR_MSG = """Le document <a target="_blank" href="{2}" title="Ce document s’ouvrira dans une nouvelle fenêtre" aria-label="Ce document s’ouvrira dans une nouvelle fenêtre">{0}</a> n'est pas exportable :
il contient des remises et les comptes RRR ne sont pas configurés.
<a onclick="window.openPopup('{1}');" href='#' title="Configurer les comptes RRR dans une nouvelle fenêtre" aria-label="Configurer les comptes RRR dans une nouvelle fenêtre">
Configurer les comptes RRR
</a>"""


class SageSingleInvoiceExportPage(BaseExportView):
    """
    Single invoice export page
    """

    admin_route_name = ACCOUNTING_INDEX_URL
    # L'interface utilisée pour plugger l'objet qui génère le fichier d'export
    writer_interface = ITreasuryInvoiceWriter

    @property
    def title(self):
        return "Export des écritures pour la facture {0}".format(
            self.context.official_number,
        )

    def populate_action_menu(self):
        """
        Add a back button to the action menu
        """
        self.request.actionmenu.add(
            ViewLink(
                label="Retour au document",
                path="/%ss/{id}/accounting" % get_task_view_type(self.context),
                id=self.context.id,
            )
        )

    def before(self):
        self.populate_action_menu()

    def validate_form(self, forms):
        """
        Return a a void form name and an appstruct so processing goes on
        """
        return "", {}

    def query(self, appstruct, formname):
        force = self.request.params.get("force", False)
        query = Task.query().with_polymorphic([CancelInvoice, Invoice])
        query = query.filter(Task.id == self.context.id)
        if not force:
            query = query.filter(
                or_(Invoice.exported == 0, CancelInvoice.exported == 0)
            )
        return query

    def _check_invoice_line(self, line):
        """
        Check the invoice line is ok for export

        :param obj line: A TaskLine instance
        """
        return line.product is not None

    def _check_num_invoices(self, invoices):
        """
        Return the number of invoices to export
        """
        return invoices.count()

    def _check_discount_config(self, internal=False):
        """
        Check that the rrr accounts are configured
        """
        if internal:
            # Pour les factures internes, on reste sur le compte cg de la tva
            check = bool(self.request.config.get("internalcompte_rrr"))
        else:
            check = self.request.config.get("compte_rrr") and self.request.config.get(
                "compte_cg_tva_rrr"
            )
        return check

    def check(self, invoices):
        """
        Check that the given invoices are 'exportable'
        """
        logger.debug("    + Checking number of invoices to export")
        logger.debug(invoices)
        count = self._check_num_invoices(invoices)
        if count == 0:
            title = "Il n'y a aucune facture à exporter"
            res = {
                "title": title,
                "errors": [],
            }
            return False, res
        logger.debug("done")
        title = "Vous vous apprêtez à exporter {0} factures".format(count)
        res = {"title": title, "errors": []}

        for invoice in invoices:
            official_number = invoice.official_number
            logger.debug("    + Checking invoice {}".format(official_number))

            # URLS
            invoice_url = get_task_url(self.request, invoice)
            company_url = get_company_url(self.request, invoice.company, action="edit")
            customer_url = self.request.route_path(
                CUSTOMER_ITEM_ROUTE, id=invoice.customer.id, _query={"action": "edit"}
            )
            if invoice.internal:
                admin_url = self.request.route_path(INTERNALINVOICE_CONFIG_URL)
            else:
                admin_url = self.request.route_path(INVOICE_CONFIG_URL)

            # CHECK PRODUCTS
            for line in invoice.all_lines:
                if not self._check_invoice_line(line):
                    set_product_url = get_task_url(
                        self.request, invoice, suffix="/set_products"
                    )
                    message = MISSING_PRODUCT_ERROR_MSG.format(
                        official_number, set_product_url, invoice_url
                    )
                    res["errors"].append(message)
                    break

            # CHECK DISCOUNTS
            if invoice.discounts:
                if not self._check_discount_config(invoice.internal):
                    message = MISSING_RRR_CONFIG_ERROR_MSG.format(
                        official_number,
                        admin_url,
                        invoice_url,
                    )
                    res["errors"].append(message)

            # CHECK COMPANY
            if not check_company_accounting_configuration(invoice.company):
                message = COMPANY_ERROR_MSG.format(
                    official_number,
                    invoice.company.name,
                    company_url,
                    invoice_url,
                )
                res["errors"].append(message)
                continue

            # CHECK CUSTOMER
            if not check_customer_accounting_configuration(
                self.request, invoice.customer, invoice
            ):
                message = CUSTOMER_ERROR_MSG.format(
                    official_number=official_number,
                    customer_label=invoice.customer.label,
                    customer_url=customer_url,
                    invoice_url=invoice_url,
                    company_url=company_url,
                    company_label=invoice.company.name,
                    admin_url=admin_url,
                    admin_tva_url=TVA_URL,
                )
                res["errors"].append(message)
                continue

        return len(res["errors"]) == 0, res

    def record_exported(self, invoices, form_name, appstruct):
        for invoice in invoices:
            ensure_task_pdf_persisted(invoice, self.request)
            logger.info(
                "The {0.type_} number {0.official_number} (id : {0.id})"
                "has been exported".format(invoice)
            )
            invoice.exported = True

            self.request.dbsession.merge(invoice)

    def record_export(self, invoices, form_name, appstruct, export_file):
        # We create an export entry
        export = InvoiceAccountingExportLogEntry()
        export.user_id = self.request.identity.id
        export.export_file_id = export_file.id
        export.export_type = ACCOUNTING_EXPORT_TYPE_INVOICES

        # For all invoices we put them inside
        for invoice in invoices:
            export.exported_invoices.append(invoice)

        # Commit changes in DB
        self.request.dbsession.add(export)
        self.request.dbsession.flush()

    def _collect_export_data(self, invoices, appstruct=None):
        """
        Produce the data to export
        """
        result = []
        # we use the same for Invoice/InternalInvoice
        Groupper = self.request.find_service_factory(
            ITreasuryGroupper,
            context=Invoice,
        )
        groupper = Groupper()

        for invoice in invoices:
            exporter = self.request.find_service(ITreasuryProducer, context=invoice)
            invoice_items = exporter.get_item_book_entries(invoice)
            invoice_groupped_items = groupper.group_items(invoice_items)

            result.extend(invoice_groupped_items)

        return result

    def get_filename(self, writer):
        return get_timestamped_filename("export_facture", writer.extension)


class SageInvoiceExportPage(SageSingleInvoiceExportPage):
    """
    Provide a sage export view compound of :
        * a form for date to date invoice exports
        * a form for number to number invoice export
    """

    @property
    def title(self):
        return "Export des écritures des factures de vente"

    def populate_action_menu(self):
        self.request.actionmenu.add(
            ViewLink(
                label="Liste des factures",
                path=INVOICE_COLLECTION_ROUTE,
            )
        )

    def get_forms(self):
        """
        Return the different invoice search forms
        """
        result = OrderedDict()
        all_form = get_invoice_all_form(self.request)
        period_form = get_invoice_period_form(self.request, all_form.counter)
        number_form = get_invoice_number_form(
            self.request,
            all_form.counter,
        )

        for form in all_form, number_form, period_form:
            result[form.formid] = {"form": form, "title": form.schema.title}

        return result

    def _filter_by_antenne(self, query, query_params_dict):
        """
        Filter regarding the antenne of the User associated to the company
        that created the document. If no user associated to the company or
        multiple user it's not taken int account
        """
        if "antenne_id" not in query_params_dict:
            return query

        antenne_id = query_params_dict["antenne_id"]
        query = Task.query_by_antenne_id(antenne_id, query)

        return query

    def _filter_by_follower(self, query, query_params_dict):
        """
        Filter regarding the follower of the User associated to the company
        that created the document. If no user associated to the company or
        multiple user it's not taken int account
        """
        if "follower_id" not in query_params_dict:
            return query

        follower_id = query_params_dict["follower_id"]
        query = Task.query_by_follower_id(follower_id, query)

        return query

    def _filter_by_auto_validated(self, query, query_params_dict):
        """
        Filter regarding if the document has been auto validated
        or not
        :param obj query: A sqlalchemy query
        :param dict appstruct: The form datas
        """
        if "only_auto_validated" in query_params_dict:
            only_auto_validated = query_params_dict.get("only_auto_validated")
            if only_auto_validated:
                query = query.filter(Task.auto_validated == 1)

        return query

    def _filter_by_validator(self, query, query_params_dict):
        """
        Filter regarding who validated the invoice
        Will only keep all expenses validated by the designated user.
        :param obj query: A sqlalchemy query
        :param dict appstruct: The form datas
        """
        if "validator_id" in query_params_dict:
            validator_id = query_params_dict["validator_id"]
            query = Task.query_by_validator_id(validator_id, query)

        return query

    def query(self, query_params_dict, form_name):
        filters = {"doctypes": query_params_dict["doctypes"]}

        if form_name == "period_form":
            filters.update(
                dict(
                    start_date=query_params_dict["start_date"],
                    end_date=query_params_dict["end_date"],
                )
            )

        elif form_name == "invoice_number_form":
            filters.update(
                dict(
                    start_number=query_params_dict["start"],
                    end_number=query_params_dict["end"],
                    year=query_params_dict["financial_year"],
                )
            )

        try:
            query = query_invoices_for_export(**filters)
        except MultipleResultsFound:
            self.request.session.flash(
                "Votre filtre n'est pas assez précis, plusieurs factures "
                "portent le même numéro, veuillez spécifier une année"
            )
            query = None

        if query:
            exported = query_params_dict.get("exported")
            if not exported:
                if query_params_dict.get("doctypes") == "internal":
                    query = query.filter(
                        or_(
                            InternalInvoice.exported == False,  # NOQA
                            InternalCancelInvoice.exported == False,  # NOQA
                        )
                    )
                elif query_params_dict.get("doctypes") == "external":
                    query = query.filter(
                        or_(
                            Invoice.exported == False,  # NOQA
                            CancelInvoice.exported == False,  # NOQA
                        )
                    )
                else:
                    query = query.filter(
                        or_(
                            Invoice.exported == False,  # NOQA
                            CancelInvoice.exported == False,  # NOQA
                            InternalInvoice.exported == False,  # NOQA
                            InternalCancelInvoice.exported == False,  # NOQA
                        )
                    )

            query = self._filter_by_validator(query, query_params_dict)
            query = self._filter_by_auto_validated(query, query_params_dict)
            query = self._filter_by_antenne(query, query_params_dict)
            query = self._filter_by_follower(query, query_params_dict)

        return query

    def check_num_invoices(self, invoices):
        return invoices.count()

    def validate_form(self, forms):
        return BaseExportView.validate_form(self, forms)


def add_routes(config):
    config.add_route("/export/treasury/invoices", "/export/treasury/invoices")
    config.add_route(
        "/export/treasury/invoices/{id}",
        "/export/treasury/invoices/{id}",
        traverse="/tasks/{id}",
    )


def add_views(config):
    config.add_view(
        SageSingleInvoiceExportPage,
        route_name="/export/treasury/invoices/{id}",
        renderer="/export/single.mako",
        permission=PERMISSIONS["global.manage_accounting"],
    )

    config.add_view(
        SageInvoiceExportPage,
        route_name="/export/treasury/invoices",
        renderer="/export/main.mako",
        permission=PERMISSIONS["global.manage_accounting"],
    )


def includeme(config):
    add_routes(config)
    add_views(config)
    config.add_admin_menu(
        parent="accounting",
        order=0,
        href="/export/treasury/invoices",
        label="Export des factures",
        permission=PERMISSIONS["global.manage_accounting"],
    )

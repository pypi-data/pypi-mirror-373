"""
Weasyprint pdf task panel
"""
import logging
from sqla_inspect.py3o import SqlaContext

from caerp.models.project import BusinessType
from caerp.models.task import (
    Invoice,
    Estimation,
    CancelInvoice,
)
from caerp.models.company import Company

from caerp.models.form_options import FormFieldDefinition
from caerp.utils.html import split_rich_text_in_blocks
from caerp.utils.strings import (
    format_quantity,
    is_hours,
)
from caerp.panels import BasePanel


logger = logging.getLogger(__name__)
CompanySerializer = SqlaContext(Company)


def pdf_header_panel(context, request):
    """
    Panel for task pdf file header
    Only shown once in the rendering (not on all pages)
    """
    result = {
        "company": context.company,
        "has_header": False,
        "config": request.config,
        "task": context,
    }
    if context.company.header_file:
        result["has_header"] = True
    return result


def pdf_footer_panel(context, request, **kwargs):
    """
    Panel for task pdf file footer

    Show on all pages
    """
    config = request.config
    result = {
        "title": config.get("coop_pdffootertitle"),
        "text": config.get("coop_pdffootertext"),
        "pdf_current_page": "",
        "pdf_page_count": "",
    }
    if context.is_training():
        result["more_text"] = config.get("coop_pdffootercourse")

    if isinstance(context, Estimation):
        number_label = "Devis {}".format(context.internal_number)
    elif context.status == "valid":
        number_label = "Facture {}".format(context.official_number)
    else:
        number_label = "Document non numéroté"

    result["number"] = number_label

    return {**result, **kwargs}


class PdfContentPanel(BasePanel):
    """
    Panel used to render the body of a Task's html representation.
    """

    def _has_multiple_tvas(self):
        # Si on a plusieurs TVA supérieur ou égale à 0 dans le document, cela
        # affecte l'affichage
        tva_values = [max(tva, 0) for tva in self.context.get_tvas()]
        return len(set(tva_values)) > 1

    def _progress_invoicing_data(self):
        """
        Manage progress invoicing related data
        """
        result = {
            "show_progress_invoicing": False,
            "show_previous_invoice": False,
        }
        if self.context.has_progress_invoicing_plan():
            result["show_progress_invoicing"] = True
            self.first_column_colspan += 2

            if self.context.business.has_previous_invoice(self.context):
                result["show_previous_invoice"] = True
                self.first_column_colspan += 1

            if (
                self.context.progress_invoicing_plan.has_deposit()
                and self.context.display_units
            ):
                self.first_column_colspan += 1

        return result

    def _mentions_data(self):
        # Contexte de templating qui sera utilisé pour les mentions et autres
        # textes configurables avec une notion de templating
        tmpl_context = CompanySerializer.compile_obj(self.context.company)
        mentions = []
        if self.context.insurance:
            mentions.append(self.context.insurance)
        mentions.extend(self.context.mandatory_mentions)
        mentions.extend(self.context.mentions)
        return {
            "mentions": mentions,
            "mention_tmpl_context": tmpl_context,
        }

    def _columns_options(self):
        has_dates = self.context.has_line_dates()
        result = {
            "ttc": self.context.display_ttc,
            "tvas": False,
            "units": self.context.display_units,
            "date": has_dates,
        }
        if self.context.has_price_study():
            # result["ttc"] = False
            result["date"] = False

        result["tvas"] = (
            self._has_multiple_tvas() and not self.context.business_type.tva_on_margin
        )

        # Calcul des nombres de colonnes
        if self.context.display_units:
            self.first_column_colspan += 4
        else:
            self.first_column_colspan += 1

        if has_dates:
            self.first_column_colspan += 1

        return result

    def __call__(self, with_cgv=True):
        """
        Panel generating the main html page for a task pdf's output
        """
        # Colspan pour la première colonne
        # Calculé au travers des différentes méthodes
        self.first_column_colspan = 0
        result = {
            "with_cgv": with_cgv,
            "config": self.request.config,
            "task": self.context,
            "groups": self.context.get_groups(),
            "project": self.context.project,
            "company": self.context.project.company,
            "is_tva_on_margin_mode": self.context.business_type.tva_on_margin,
        }
        result.update(self._progress_invoicing_data())
        result.update(self._mentions_data())
        result["columns"] = self._columns_options()
        result["columns"]["first_column_colspan"] = self.first_column_colspan
        result["custom_labels"] = FormFieldDefinition.get_form_labels("task")

        return result


class TaskLineGroupPanel(BasePanel):
    """
    A panel building the context to render a TaskLineGroup
    Expects the following parameters

    :param obj context: The current task to be rendered
    :param request: The Pyramid request
    :param obj group: A TaskLineGroup
    :param column: Options related to columns
    :param show_previous_invoice: Show task line invoiced progress (already invoiced)
    :param show_progress_invoicing: Show task line progress percentage
    :param is_tva_on_margin_mode: Is the Vta collected on margin
    """

    def _get_line_panel_name(self, line):
        panel_name = "task_pdf_task_line"
        if self.context.has_price_study():
            from caerp.models.price_study import PriceStudyWork

            if isinstance(line.price_study_product, PriceStudyWork):
                if line.price_study_product.display_details:
                    panel_name = "price_study_pdf_work_details"
                else:
                    panel_name = "price_study_pdf_work_resume"
        if self.context.has_progress_invoicing_plan():
            from caerp.models.progress_invoicing import ProgressInvoicingWork

            if isinstance(line.progress_invoicing_product, ProgressInvoicingWork):
                panel_name = "progress_invoicing_pdf_work_details"
            else:
                panel_name = "progress_invoicing_pdf_product"

        return panel_name

    def __call__(self, **options):
        self.group = options["group"]
        result = options
        result["task"] = self.context
        result["display_subtotal"] = len(self.context.get_groups()) > 1
        result["get_line_panel_name"] = self._get_line_panel_name

        if self.context.has_progress_invoicing_plan():
            result["has_deposit"] = self.context.progress_invoicing_plan.has_deposit()

        # Si possible on splitte la description pour éviter le chevauchement des pages
        if self.group.description:
            result["description_lines"] = split_rich_text_in_blocks(
                self.group.description
            )
            result["title"] = self.group.title
        else:
            result["description_lines"] = [f"<strong>{self.group.title}</strong>"]
            result["title"] = None

        return result


class TaskLineGroupResumePanel(TaskLineGroupPanel):
    def __call__(self, **options):
        result = super().__call__(**options)
        result["total"] = self.group.total_ttc()
        result["total_ht"] = self.group.total_ht()
        result["quantity"] = 1
        result["unity"] = "-"
        result["unit_ht"] = self.group.total_ht()
        tvas = list(self.group.get_tvas().keys())
        if len(tvas) == 1:
            result["tva"] = tvas[0]
        else:
            result["tva"] = None
        return result


class TaskLinePanel(BasePanel):
    """
    A panel representing a single TaskLine

    :param obj context: The current task to be rendered
    :param request:
    :param obj line: A taskline
    :param show_previous_invoice: Show task line invoiced progress (already
    invoiced)
    :param show_progress_invoicing: Show task line progress percentage
    :return:
    """

    def _get_unit_details(self):
        """
        Collect data to display the units computation
        """
        quantity = self.line.quantity
        unity = self.line.unity
        ttc_mode = self.context.mode == "ttc"
        show_ttc_col = self.options["columns"]["ttc"]
        tva_on_margin = self.options["is_tva_on_margin_mode"]

        if tva_on_margin:
            if ttc_mode:
                unit_ht = self.line.cost
            elif self.line.tva > 0:
                # Only TVA 20% and exo are supported in tva_on_margin mode
                unit_ht = self.line.cost * 1.2
            else:
                unit_ht = self.line.unit_ht()

        elif ttc_mode and show_ttc_col:
            unit_ht = self.line.cost

        else:
            unit_ht = self.line.unit_ht()
        return {"quantity": quantity, "unit_ht": unit_ht, "unity": unity}

    def _get_totals(self):
        return dict(
            total=self.line.total(),
            total_ht=self.line.total_ht(),
        )

    def _get_tva(self):
        """
        Returns the Tva and converts tvas lower than 0 to 0
        """
        return max(self.line.tva, 0)

    def __call__(self, **options):
        self.line = options["line"]

        result = self.options = options
        result["task"] = self.context

        result["description_lines"] = split_rich_text_in_blocks(self.line.description)

        if options["columns"]["units"]:
            result.update(self._get_unit_details())
        if options["columns"]["tvas"]:
            result["tva_value"] = self._get_tva()
        if options["columns"]["date"]:
            result["date"] = self.line.date

        result.update(self._get_totals())
        return result


class DiscountLinePanel(TaskLinePanel):
    def __call__(self, **options):
        self.line = options["discount"]
        result = self.options = options

        result["task"] = self.context
        result["description"] = self.line.description
        if options["columns"]["tvas"]:
            result["tva_value"] = self._get_tva()
        result["total"] = self.line.total() * -1
        result["total_ht"] = self.line.total_ht() * -1
        return result


class PostTTCLinePanel(TaskLinePanel):
    def __call__(self, **options):
        self.line = options["post_ttc_line"]
        result = self.options = options

        result["task"] = self.context
        result["label"] = self.line.label
        result["amount"] = self.line.amount
        return result


class PriceStudyWorkResumePanel(TaskLinePanel):
    def _get_totals(self):
        return {"total_ht": self.work.total_ht, "total": self.work.ttc()}

    def _get_unit_details(self):
        quantity = self.work.quantity
        unity = self.work.unity
        if self.price_study.mask_hours and is_hours(unity):
            unity = "forfait"
        unit_ht = self.work.ht
        return {"quantity": quantity, "unit_ht": unit_ht, "unity": unity}

    def __call__(self, **options):
        self.work = options["line"].price_study_product
        self.price_study = self.work.price_study
        assert self.work is not None, (
            "La TaskLine n'a pas de PriceStudyWork associé, on n'aurait jamais dû"
            " arriver ici"
        )
        return super().__call__(**options)


class PriceStudyWorkDetailsPanel(PriceStudyWorkResumePanel):
    def __call__(self, **options):
        self.work = options["line"].price_study_product
        assert (
            self.work.tva
        ), f"Le PriceStudyWork {self.work.id} n'a pas de tva de configurée"
        self.price_study = self.work.price_study

        result = self.options = options
        # # On splitte la description pour éviter le chevauchement des pages
        # # (autant que possible)
        result["description_lines"] = split_rich_text_in_blocks(self.work.description)

        if options["columns"]["units"]:
            result.update(self._get_unit_details())
        result.update(self._get_totals())
        result["work"] = self.work
        result["task"] = self.context
        if options["columns"]["tvas"]:
            result["tva_value"] = max(self.work.tva.value, 0)
        return result


class PriceStudyWorkItemPanel(BasePanel):
    """
    Panel présentant un WorkItem d'une étude de prix
    """

    def _get_unit_details(self):
        unity = self.work_item.unity
        if self.price_study.mask_hours and is_hours(unity):
            # On masque les heures et le détail du calcul
            unity = "forfait"
            quantity = "1"
            unit_ht = self.work_item.total_ht
        else:
            unit_ht = self.work_item.ht
            quantity = format_quantity(self.work_item.total_quantity)

        return {"quantity": quantity, "unit_ht": unit_ht, "unity": unity}

    def __call__(self, **options):
        self.work_item = options["work_item"]
        self.work = options["work"]
        self.price_study = options["work"].price_study
        result = options
        if options["columns"]["units"]:
            result.update(self._get_unit_details())
        result["description_lines"] = split_rich_text_in_blocks(
            self.work_item.description
        )
        result["total_ht"] = self.work_item.total_ht
        result["total"] = self.work_item.ttc()
        result["task"] = self.context
        return result


class ProgressInvoicingProductPanel(TaskLinePanel):
    def _get_progress_invoicing_options(self):
        result = {}
        result["percentage"] = self.product.percentage
        result["invoiced_percentage"] = self.product.already_invoiced
        result["left_percentage"] = self.product.get_percent_left()
        return result

    def __call__(self, **options):
        result = super().__call__(**options)
        self.product = self.line.progress_invoicing_product
        result.update(self._get_progress_invoicing_options())
        result["product"] = self.product
        if options["columns"]["units"]:
            result["quantity"] = self.product.status.source_task_line.quantity
            result["unit_ht"] = self.product.status.source_task_line.unit_ht()
            result["has_deposit"] = self.product.status.has_deposit()
            if result["has_deposit"]:
                result["deposit"] = self.product.status.total_deposit()
        return result


class ProgressInvoicingWorkDetailsPanel(ProgressInvoicingProductPanel):
    def _get_progress_invoicing_options(self):
        result = super()._get_progress_invoicing_options()
        # Si le Work n'est pas 'locked', on affiche le pourcentage par ligne uniquem
        if not self.product.locked:
            result["percentage"] = None
            result["invoiced_percentage"] = None
            result["left_percentage"] = None
        result["work"] = self.product
        return result


class ProgressInvoicingWorkItemPanel(BasePanel):
    """
    Panel présentant l'avancement d'un WorkItem

    NB : Le devis d'origine avait une étude de prix
    """

    def _get_percents(self):
        result = {
            "percentage": self.work_item.percentage,
            "invoiced_percentage": self.work_item.already_invoiced,
            "left_percentage": self.work_item.get_percent_left(),
        }
        return result

    def _get_unit_details(self):
        unity = self.source_work_item.unity
        if self.price_study.mask_hours and is_hours(unity):
            # On masque les heures et le détail du calcul
            unity = "forfait"
            quantity = 1
            unit_ht = self.source_work_item.total_ht
        else:
            unit_ht = self.source_work_item.ht
            quantity = self.source_work_item.total_quantity

        return {"quantity": quantity, "unit_ht": unit_ht, "unity": unity}

    def __call__(self, **options):
        self.work_item = options["work_item"]
        self.work = options["work"]
        self.source_work_item = self.work_item.status.price_study_work_item
        self.price_study = self.source_work_item.get_price_study()

        result = options
        if options["columns"]["units"]:
            result["has_deposit"] = self.work_item.status.has_deposit()
            if result["has_deposit"]:
                result["deposit"] = self.work_item.status.total_deposit()
            result.update(self._get_unit_details())

        result["description_lines"] = split_rich_text_in_blocks(
            self.source_work_item.description
        )
        result.update(self._get_percents())
        result["total_ht"] = self.work_item.total_ht()
        if options["columns"]["tvas"]:
            result["total"] = self.work_item.total_tva(result["total_ht"])
        if options["columns"]["ttc"]:
            result["total"] = self.work_item.total_ttc(result["total_ht"])

        result["task"] = self.context
        result["work_item"] = True
        return result


def pdf_cgv_panel(context, request):
    """
    Panel used to render cgv
    """
    business_type: BusinessType = getattr(context, "business_type", None)
    if business_type and business_type.coop_cgv_override:
        cae_cgv = business_type.coop_cgv_override
    else:
        cae_cgv = request.config.get("coop_cgv")
    company_cgv = context.company.cgv
    return dict(cae_cgv=cae_cgv, company_cgv=company_cgv)


def pdf_content_wrapper_panel(context, request):
    """
    Used to wrap the content inside an html page structure
    """
    return dict(task=context)


def includeme(config):
    config.add_panel(
        pdf_header_panel,
        "task_pdf_header",
        renderer="panels/task/pdf/header.mako",
    )
    config.add_panel(
        pdf_footer_panel,
        "task_pdf_footer",
        renderer="panels/task/pdf/footer.mako",
    )
    for document_type in (Estimation, Invoice, CancelInvoice):
        panel_name = "task_pdf_content"
        template = "panels/task/pdf/{0}_content.mako".format(
            document_type.__tablename__
        )
        config.add_panel(
            PdfContentPanel,
            panel_name,
            context=document_type,
            renderer=template,
        )

    config.add_panel(
        pdf_content_wrapper_panel,
        "task_pdf_content",
        renderer="panels/task/pdf/content_wrapper.mako",
    )
    config.add_panel(
        TaskLineGroupPanel,
        "task_pdf_task_line_group",
        renderer="panels/task/pdf/task_line_group.mako",
    )
    config.add_panel(
        TaskLineGroupResumePanel,
        "task_pdf_task_line_group_resume",
        renderer="panels/task/pdf/task_line_group_resume.mako",
    )
    config.add_panel(
        TaskLinePanel,
        "task_pdf_task_line",
        renderer="panels/task/pdf/task_line.mako",
    )
    config.add_panel(
        DiscountLinePanel,
        "task_pdf_discount_line",
        renderer="panels/task/pdf/discount_line.mako",
    )
    config.add_panel(
        PostTTCLinePanel,
        "task_pdf_post_ttc_line",
        renderer="panels/task/pdf/post_ttc_line.mako",
    )
    config.add_panel(
        pdf_cgv_panel,
        "task_pdf_cgv",
        renderer="panels/task/pdf/cgv.mako",
    )
    # Panels spécifiques aux études de prix
    config.add_panel(
        PriceStudyWorkResumePanel,
        "price_study_pdf_work_resume",
        renderer="panels/task/pdf/task_line.mako",
    )
    config.add_panel(
        PriceStudyWorkDetailsPanel,
        "price_study_pdf_work_details",
        renderer="panels/task/pdf/price_study/work_details.mako",
    )
    config.add_panel(
        PriceStudyWorkItemPanel,
        "price_study_pdf_work_item",
        renderer="panels/task/pdf/price_study/work_item.mako",
    )
    # Panels spécifiques à la facturation à l'avancement
    config.add_panel(
        ProgressInvoicingProductPanel,
        "progress_invoicing_pdf_product",
        renderer="panels/task/pdf/progress_invoicing/product.mako",
    )
    config.add_panel(
        ProgressInvoicingWorkDetailsPanel,
        "progress_invoicing_pdf_work_details",
        renderer="panels/task/pdf/progress_invoicing/work_details.mako",
    )
    config.add_panel(
        ProgressInvoicingWorkItemPanel,
        "progress_invoicing_pdf_work_item",
        renderer="panels/task/pdf/progress_invoicing/product.mako",
    )

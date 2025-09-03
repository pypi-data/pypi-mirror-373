import colander
import logging

from caerp.consts.permissions import PERMISSIONS
from sqlalchemy import (
    distinct,
    select,
    or_,
)
from sqlalchemy.orm import (
    selectinload,
    joinedload,
)

from caerp.forms.business.business import get_business_list_schema
from caerp.models.company import Company
from caerp.models.indicators import CustomBusinessIndicator
from caerp.models.project import Project
from caerp.models.project.business import Business
from caerp.models.project.types import BusinessType
from caerp.models.task import (
    Task,
    Invoice,
)
from caerp.models.third_party.customer import Customer
from caerp.models.training.bpf import BusinessBPFData
from caerp.utils.widgets import Link
from caerp.views import (
    BaseListView,
    TreeMixin,
)
from caerp.views.business.routes import (
    COMPANY_BUSINESSES_ROUTE,
    BUSINESS_ITEM_ROUTE,
    BUSINESSES_ROUTE,
)


logger = logging.getLogger(__name__)


class BusinessListTools:
    def query(self):
        query = self.dbsession.query(distinct(Business.id), Business)
        query = query.outerjoin(Business.project).join(Project.company)
        query = query.options(
            selectinload(Business.tasks)
            .selectinload(Project.customers)
            .load_only(Customer.id, Customer.label),
            selectinload(Business.invoices_only).load_only(
                Invoice.financial_year,
            ),
            joinedload(Business.business_type).load_only("id", "bpf_related"),
            selectinload(Business.bpf_datas),
        )
        query = query.filter(Business.visible == True)
        query = query.order_by(Business.id.desc())
        return query

    def filter_search(self, query, appstruct):
        search = appstruct.get("search", None)
        if search not in (None, colander.null, ""):
            logger.debug("  + Filtering on search")
            query = query.outerjoin(Business.tasks)
            query = query.filter(
                or_(
                    Business.tasks.any(
                        or_(
                            Task.official_number.like(f"%{search}%"),
                            Task.internal_number.like(f"%{search}%"),
                        )
                    ),
                    Business.name.like(f"%{search}%"),
                )
            )
        return query

    def filter_invoicing_year(self, query, appstruct):
        invoicing_year = appstruct.get("invoicing_year", -1)
        if invoicing_year not in (-1, colander.null):
            logger.debug("  + Filtering on invoicing_year")
            query = query.filter(
                Business.invoices_only.any(
                    Invoice.financial_year == invoicing_year,
                )
            )
        return query

    def filter_business_type_id(self, query, appstruct):
        business_type_id = appstruct.get("business_type_id")
        if business_type_id not in ("all", None):
            logger.debug("  + Filtering on business_type_id")
            query = query.filter(Business.business_type_id == business_type_id)
        return query

    def filter_company_id(self, query, appstruct):
        company_id = appstruct.get("company_id", None)
        if company_id not in (None, "", colander.null):
            logger.debug("  + Filtering on company_id")
            query = query.filter(Project.company_id == company_id)
        return query

    def filter_antenne_id(self, query, appstruct):
        antenne_id = appstruct.get("antenne_id", None)
        if antenne_id not in (None, "", colander.null):
            logger.debug("  + Filtering on antenne_id")
            query = query.filter(Company.antenne_id == antenne_id)
        return query

    def filter_customer_id(self, query, appstruct):
        customer_id = appstruct.get("customer_id", None)
        if customer_id not in (None, "", colander.null):
            logger.debug("  + Filtering on customer_id")
            query = query.outerjoin(Business.tasks)
            query = query.filter(Business.tasks.any(Task.customer_id == customer_id))
        return query

    """
    TODO Ajouter un filtre sur l'état des fichiers de l'affaire
    def filter_sale_file_requirements(self, query, appstruct):
        sale_file_requirements = appstruct.get("sale_file_requirements", None)
        if sale_file_requirements not in (None, "", colander.null):
            logger.debug("  + Filtering on sale file requirements")
            [...]
            if sale_file_requirements == "success":
                pass
            if sale_file_requirements == "danger":
                pass
            if sale_file_requirements == "wait":
                pass
            if sale_file_requirements == "forced":
                pass
        return query
    """

    def filter_bpf_filled(self, query, appstruct):
        """
        Double behaviour :
        -  if a year is selected, check bpf_filled for that given year (see
          filter_invoicing_year)
        -  else check global bpf_filled indicator
        """
        invoicing_year = appstruct.get("invoicing_year", -1)
        bpf_filled = appstruct.get("bpf_filled", None)

        if bpf_filled:
            if bpf_filled == "no":
                query = query.join(Business.business_type)
                query = query.filter(BusinessType.bpf_related == False)
            else:
                if bpf_filled == "yes":
                    query = query.join(Business.business_type)
                    query = query.filter(BusinessType.bpf_related == True)
                if invoicing_year != -1:
                    logger.debug(
                        "  + Filtering on bpf status for year {}".format(invoicing_year)
                    )
                    query.join(BusinessBPFData, isouter=True)
                    year_filter = Business.bpf_datas.any(
                        BusinessBPFData.financial_year == invoicing_year
                    )
                    if bpf_filled == "full":
                        query = query.filter(year_filter)
                    if bpf_filled == "partial":
                        query = query.filter(~year_filter)
                else:
                    logger.debug("  + Filtering on bpf status for all years")
                    query = query.join(CustomBusinessIndicator, isouter=True,).filter(
                        CustomBusinessIndicator.name == "bpf_filled",
                    )

                    if bpf_filled == "full":
                        query = query.filter(
                            CustomBusinessIndicator.status
                            == CustomBusinessIndicator.SUCCESS_STATUS
                        )
                    if bpf_filled == "partial":
                        query = query.filter(
                            CustomBusinessIndicator.status.in_(
                                [
                                    CustomBusinessIndicator.DANGER_STATUS,
                                    CustomBusinessIndicator.WARNING_STATUS,
                                ]
                            )
                        )

        return query

    """
    TODO Faire fonctionner le filtre sur l'état de facturation de l'affaire (indicateurs nok)
    def filter_include_completed(self, query, appstruct):
        include_completed = appstruct.get("include_completed", True)
        if not include_completed:
            logger.debug("  + Filtering on completed businesses")
            subquery = (
                select(distinct(CustomBusinessIndicator.business_id))
                .where(CustomBusinessIndicator.name == "invoiced")
                .where(CustomBusinessIndicator.status == "success")
            )
            query = query.filter(Business.id.notin_(subquery))
        return query
    """

    def filter_include_resulted(self, query, appstruct):
        include_resulted = appstruct.get("include_resulted", True)
        if not include_resulted:
            logger.debug("  + Filtering on resulted businesses")
            subquery = select(distinct(Invoice.business_id)).where(
                Invoice.paid_status != "resulted"
            )
            query = query.filter(Business.id.in_(subquery))
        return query


class GlobalBusinessListView(BusinessListTools, BaseListView):
    is_admin = True
    title = "Liste des affaires de la CAE"
    add_template_vars = ("is_admin", "stream_actions")

    def get_schema(self):
        return get_business_list_schema(self.request, is_global=self.is_admin)

    def stream_actions(self, item):
        yield Link(
            self.request.route_path(
                BUSINESS_ITEM_ROUTE,
                id=item.id,
            ),
            "Voir l'affaire",
            icon="arrow-right",
            css="icon",
        )


class CompanyBusinessListView(GlobalBusinessListView, TreeMixin):
    is_admin = False

    @property
    def title(self):
        return f"Liste des affaires de l'enseigne {self.request.context.name}"

    def filter_company_id(self, query, appstruct):
        query = query.filter(Project.company_id == self.request.context.id)
        return query


def includeme(config):
    config.add_view(
        GlobalBusinessListView,
        route_name=BUSINESSES_ROUTE,
        renderer="/business/list_businesses.mako",
        permission=PERMISSIONS["global.list_invoices"],
    )
    config.add_view(
        CompanyBusinessListView,
        route_name=COMPANY_BUSINESSES_ROUTE,
        renderer="/business/list_businesses.mako",
        permission=PERMISSIONS["company.view"],
        context=Company,
    )
    config.add_admin_menu(
        parent="sale",
        order=0,
        label="Affaires",
        href=BUSINESSES_ROUTE,
        permission=["global.list_invoices"],
    )
    config.add_company_menu(
        parent="sale",
        order=1,
        label="Affaires",
        route_name=COMPANY_BUSINESSES_ROUTE,
        route_id_key="company_id",
        routes_prefixes=[BUSINESS_ITEM_ROUTE],
        permission=PERMISSIONS["company.view"],
    )

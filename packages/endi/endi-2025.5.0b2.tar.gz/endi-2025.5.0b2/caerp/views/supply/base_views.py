import colander
import datetime
import logging

from sqlalchemy import select, func

from caerp.models.company import Company
from caerp.models.third_party.supplier import Supplier


logger = logging.getLogger(__name__)


class SupplierDocListTools:
    """
    Filtering tools common to SupplierInvoice and SupplierOrder

    Inheriting child must define those attributes:
    - model_class: target model class (that model_class must define a filter_by_year() method)
    - model_class_date_field : the model's field for document's date
    - line_model_class: target model class for model_class's lines
    - line_model_parent_field: the lines model's field that link parent model_class
    """

    sort_columns = {
        "company_id": "company_id",
        "date": "date",
        "name": "name",
        "supplier": "supplier_id",
        "created_at": "created_at",
    }

    default_sort = "created_at"
    default_direction = "desc"

    def filter_name(self, records, appstruct):
        search = appstruct.get("search")
        if search:
            records = records.join("supplier")
            return records.filter(
                self.model_class.name.like("%{}%".format(search))
                | Supplier.company_name.like("%{}%".format(search))
            )
        else:
            return records

    def filter_supplier(self, records, appstruct):
        supplier_id = appstruct.get("supplier_id")
        if supplier_id:
            return records.filter(
                self.model_class.supplier_id == supplier_id,
            )
        else:
            return records

    def filter_company(self, query, appstruct):
        company_id = appstruct.get("company_id")
        if company_id:
            query = query.filter(self.model_class.company_id == company_id)
        return query

    def filter_antenne_id(self, query, appstruct):
        antenne_id = appstruct.get("antenne_id")
        if antenne_id not in (None, colander.null):
            query = query.filter(Company.antenne_id == antenne_id)
        return query

    def filter_status(self, query, appstruct):
        status = appstruct.get("status")
        if status and (status != "all"):
            query = query.filter(
                self.model_class.status == status,
            )
        return query

    def filter_year(self, query, appstruct):
        year = appstruct.get("year")
        if year and year not in (-1, colander.null):
            query = self.model_class.filter_by_year(query, year)
            self.year = year
        else:
            self.year = datetime.date.today().year
        return query

    def filter_doctype(self, query, appstruct):
        type_ = appstruct.get("doctype")
        if type_ in (
            "supplier_invoice",
            "internalsupplier_invoice",
            "supplier_order",
            "internalsupplier_order",
        ):
            query = query.filter(self.model_class.type_ == type_)
        return query

    def filter_period(self, query, appstruct):
        period = appstruct.get("period", {})
        if period.get("start") not in (colander.null, None):
            start = period.get("start")
            end = period.get("end")
            if end in (None, colander.null):
                end = datetime.date.today()
            logger.debug(f"  + Filtering by period : {start} -> {end}")
            model_date = getattr(self.model_class, self.model_class_date_field)
            query = query.filter(model_date.between(start, end))
        return query

    def filter_ttc(self, query, appstruct):
        ttc = appstruct.get("ttc", {})
        if ttc.get("start") not in (None, colander.null):
            logger.info("  + Filtering by ttc amount : %s" % ttc)
            ttc_min = ttc.get("start")
            ttc_max = ttc.get("end")
            model_id = getattr(self.line_model_class, self.line_model_parent_field)
            subq = (
                select(
                    model_id.label("model_id"),
                    func.sum(
                        self.line_model_class.ht + self.line_model_class.tva
                    ).label("total"),
                )
                .group_by("model_id")
                .subquery()
            )
            query = query.join(subq, self.model_class.id == subq.c.model_id)
            if ttc_max in (None, colander.null):
                query = query.filter(subq.c.total >= ttc_min / 1000)
            else:
                query = query.filter(
                    subq.c.total.between(ttc_min / 1000, ttc_max / 1000)
                )
        return query

    def filter_expense_type(self, query, appstruct):
        expense_type_id = appstruct.get("expense_type_id")
        if expense_type_id not in (None, colander.null, "-1", -1):
            logger.info("  + Filtering by expense type : %s" % expense_type_id)
            model_id = getattr(self.line_model_class, self.line_model_parent_field)
            subq = (
                select(model_id.label("model_id"))
                .filter(self.line_model_class.type_id == expense_type_id)
                .subquery()
            )
            query = query.join(subq, self.model_class.id == subq.c.model_id)
        return query

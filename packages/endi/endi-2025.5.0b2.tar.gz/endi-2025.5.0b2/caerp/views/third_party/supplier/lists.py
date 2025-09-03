"""
    Supplier views
"""

import logging
import colander

from caerp.consts.permissions import PERMISSIONS
from sqlalchemy import (
    or_,
    not_,
)
from sqlalchemy.orm import undefer_group
from caerp.models.third_party.supplier import Supplier
from caerp.utils.widgets import (
    Link,
    POSTButton,
)
from caerp.forms.third_party.supplier import (
    get_list_schema,
)
from caerp.models.company import Company
from caerp.views import (
    BaseListView,
    BaseCsvView,
)
from .base import get_supplier_form

logger = log = logging.getLogger(__name__)


class SuppliersListTools(object):
    """
    Supplier list tools
    """

    title = "Liste des fournisseurs"
    schema = get_list_schema()
    sort_columns = {
        "label": Supplier.label,
        "code": Supplier.code,
        "company_name": Supplier.company_name,
        "created_at": Supplier.created_at,
    }
    default_sort = "created_at"
    default_direction = "desc"

    def query(self):
        company = self.request.context
        return Supplier.query().filter_by(company_id=company.id)

    def filter_archived(self, query, appstruct):
        archived = appstruct.get("archived", False)
        if archived in (False, colander.null, "false"):
            query = query.filter_by(archived=False)
        return query

    def filter_name_or_contact(self, records, appstruct):
        """
        Filter the records by supplier name or contact lastname
        """
        search = appstruct.get("search")
        if search:
            records = records.filter(
                or_(
                    Supplier.label.like("%" + search + "%"),
                    Supplier.lastname.like("%" + search + "%"),
                )
            )
        return records

    def filter_internal(self, query, appstruct):
        include_internal = appstruct.get("internal", True)
        if include_internal in (False, colander.null, "false"):
            query = query.filter(not_(Supplier.type == "internal"))
        return query


class SuppliersListView(SuppliersListTools, BaseListView):
    """
    Supplier listing view
    """

    add_template_vars = (
        "stream_actions",
        "title",
        "forms",
    )

    @property
    def forms(self):
        res = []
        form_title = "Fournisseur"
        form = get_supplier_form(self.request)
        res.append((form_title, form))
        return res

    def stream_actions(self, supplier):
        """
        Return action buttons with permission handling
        """

        if self.request.has_permission(
            PERMISSIONS["context.delete_supplier"], supplier
        ):
            yield POSTButton(
                self.request.route_path(
                    "supplier",
                    id=supplier.id,
                    _query=dict(action="delete"),
                ),
                "Supprimer",
                title="Supprimer définitivement ce fournisseur",
                icon="trash-alt",
                css="negative",
                confirm="Êtes-vous sûr de vouloir supprimer ce fournisseur ?",
            )

        yield Link(
            self.request.route_path("supplier", id=supplier.id),
            "Voir",
            title="Voir ou modifier ce fournisseur",
            icon="arrow-right",
        )

        if supplier.archived:
            label = "Désarchiver"
        else:
            label = "Archiver"
        yield POSTButton(
            self.request.route_path(
                "supplier",
                id=supplier.id,
                _query=dict(action="archive"),
            ),
            label,
            icon="archive",
        )


class SuppliersCsv(SuppliersListTools, BaseCsvView):
    """
    Supplier csv view
    """

    model = Supplier

    @property
    def filename(self):
        return "fournisseurs.csv"

    def query(self):
        company = self.request.context
        query = Supplier.query().options(undefer_group("edit"))
        return query.filter(Supplier.company_id == company.id)


def includeme(config):
    config.add_view(
        SuppliersListView,
        route_name="company_suppliers",
        renderer="suppliers.mako",
        request_method="GET",
        context=Company,
        permission=PERMISSIONS["company.view"],
    )

    config.add_view(
        SuppliersCsv,
        route_name="suppliers.csv",
        request_method="GET",
        context=Company,
        permission=PERMISSIONS["company.view"],
    )

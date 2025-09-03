import datetime

from pyramid.httpexceptions import HTTPFound
from typing import Dict

from caerp.consts.permissions import PERMISSIONS
from caerp.forms.supply.supplier_order import (
    get_supplier_orders_list_schema,
    get_supplier_order_add_schema,
)
from caerp.models.supply import (
    SupplierInvoice,
    SupplierOrder,
    SupplierOrderLine,
)
from caerp.models.third_party.supplier import Supplier
from caerp.resources import supplier_order_resources
from caerp.utils.widgets import (
    ViewLink,
    Link,
    POSTButton,
)
from caerp.views import (
    BaseFormView,
    BaseListView,
    BaseView,
    DeleteView,
    DuplicateView,
    submit_btn,
    JsAppViewMixin,
)
from caerp.views.files.views import FileUploadView
from caerp.views.supply.base_views import SupplierDocListTools
from caerp.views.supply.orders.routes import (
    COLLECTION_ROUTE,
    ITEM_ROUTE,
    COMPANY_COLLECTION_ROUTE,
)
from caerp.views.supply.utils import get_supplier_doc_url


def populate_actionmenu(request):
    return request.actionmenu.add(
        ViewLink(
            "Revenir à la liste des commandes fournisseur",
            path=COMPANY_COLLECTION_ROUTE,
            id=request.context.get_company_id(),
        )
    )


def _default_order_name(supplier):
    return "Commande {}, {}".format(
        supplier.label,
        datetime.date.today(),
    )


class SupplierOrderAddView(BaseFormView):
    add_template_vars = ("title",)
    title = "Saisir une commande fournisseur"

    schema = get_supplier_order_add_schema()
    buttons = (submit_btn,)

    def before(self, form):
        assert self.context.__name__ == "company"
        form.set_appstruct({"company_id": self.context.id})

    def submit_success(self, appstruct):
        assert self.context.__name__ == "company"
        appstruct["company_id"] = self.context.id

        supplier = Supplier.get(appstruct["supplier_id"])

        appstruct["name"] = _default_order_name(supplier)

        obj = SupplierOrder(**appstruct)

        self.dbsession.add(obj)
        self.dbsession.flush()
        edit_url = get_supplier_doc_url(
            self.request,
            doc=obj,
        )
        return HTTPFound(edit_url)


class SupplierOrderEditView(BaseView, JsAppViewMixin):
    """
    Can act as edit view or readonly view (eg: waiting for validation).
    """

    def context_url(self, _query: Dict[str, str] = {}):
        return get_supplier_doc_url(self.request, _query=_query, api=True)

    @property
    def title(self):
        label = self.context.name
        if self.context.internal:
            label += " (Commande interne)"
        return label

    def more_js_app_options(self):
        return dict(
            edit=bool(
                self.request.has_permission(PERMISSIONS["context.edit_supplier_order"])
            ),
        )

    def __call__(self):
        populate_actionmenu(self.request)
        supplier_order_resources.need()
        return dict(
            title=self.title,
            context=self.context,
            js_app_options=self.get_js_app_options(),
        )


class SupplierOrderDuplicateView(DuplicateView):
    route_name = ITEM_ROUTE
    message = "vous avez été redirigé vers la nouvelle commande fournisseur"

    def on_duplicate(self, item):
        src_order = self.context
        target_order = item

        target_order.name = "Copie de {}".format(src_order.name)
        target_order.import_lines_from_order(src_order)
        self.dbsession.merge(target_order)
        self.dbsession.flush()


class SupplierOrderListTools(SupplierDocListTools):
    model_class = SupplierOrder
    model_class_date_field = "created_at"
    line_model_class = SupplierOrderLine
    line_model_parent_field = "supplier_order_id"

    sort_columns = {
        "cae_percentage": "cae_percentage",
        "supplier_invoice": "supplier_invoice_id",
    }
    sort_columns.update(SupplierDocListTools.sort_columns)

    def filter_invoice_status(self, query, appstruct):
        invoice_status = appstruct["invoice_status"]
        if invoice_status in ("present", "draft", "valid", "resulted"):
            query = query.filter(SupplierOrder.supplier_invoice_id != None)  # noqa
            query = query.join(SupplierOrder.supplier_invoice)
            if invoice_status == "draft":
                query = query.filter(SupplierInvoice.status == "draft")
            elif invoice_status == "valid":
                query = query.filter(SupplierInvoice.status == "valid")
            elif invoice_status == "resulted":
                query = query.filter(SupplierInvoice.paid_status == "resulted")
        elif invoice_status == "absent":
            query = query.filter(SupplierOrder.supplier_invoice_id == None)  # noqa
        return query


def stream_supplier_order_actions(request, supplier_order):
    yield Link(
        get_supplier_doc_url(request, doc=supplier_order),
        "Voir ou modifier",
        icon="arrow-right",
    )
    delete_allowed = request.has_permission(
        PERMISSIONS["context.delete_supplier_order"],
        supplier_order,
    )
    if delete_allowed:
        yield POSTButton(
            get_supplier_doc_url(
                request,
                doc=supplier_order,
                _query=dict(action="delete"),
            ),
            "Supprimer",
            title="Supprimer définitivement cette commande ?",
            icon="trash-alt",
            css="negative",
            confirm="Êtes-vous sûr de vouloir supprimer cette commande ?",
        )


class BaseSupplierOrderListView(
    SupplierOrderListTools,
    BaseListView,
):
    title = "Liste des commandes fournisseurs"
    add_template_vars = ["title", "stream_actions"]
    is_admin_view = False

    def get_schema(self):
        return get_supplier_orders_list_schema(
            self.request, is_global=self.is_admin_view
        )

    def stream_actions(self, supplier_order):
        return stream_supplier_order_actions(self.request, supplier_order)


class AdminSupplierOrderListView(BaseSupplierOrderListView):
    """
    Admin-level view, listing all orders from all companies.
    """

    is_admin_view = True
    add_template_vars = BaseSupplierOrderListView.add_template_vars + [
        "is_admin_view",
    ]

    def query(self):
        return SupplierOrder.query().join(SupplierOrder.company)


class CompanySupplierOrderListView(BaseSupplierOrderListView):
    """
    Company-scoped SupplierOrder list view.
    """

    is_admin_view = False

    def query(self):
        company = self.request.context
        return SupplierOrder.query().filter(SupplierOrder.company_id == company.id)


class SupplierOrderDeleteView(DeleteView):
    delete_msg = "La commande fournisseur a bien été supprimée"

    def redirect(self):
        return HTTPFound(
            self.request.route_path(
                COMPANY_COLLECTION_ROUTE, id=self.context.company.id
            )
        )


def includeme(config):
    # Admin views
    config.add_view(
        AdminSupplierOrderListView,
        request_method="GET",
        route_name=COLLECTION_ROUTE,
        permission=PERMISSIONS["global.list_supplier_orders"],
        renderer="/supply/supplier_orders.mako",
    )

    # Company views
    config.add_view(
        SupplierOrderAddView,
        route_name=COMPANY_COLLECTION_ROUTE,
        request_param="action=new",
        permission=PERMISSIONS["context.add_supplier_order"],
        renderer="base/formpage.mako",
    )

    config.add_view(
        CompanySupplierOrderListView,
        route_name=COMPANY_COLLECTION_ROUTE,
        request_method="GET",
        renderer="/supply/supplier_orders.mako",
        permission=PERMISSIONS["company.view"],
    )
    config.add_view(
        SupplierOrderEditView,
        route_name=ITEM_ROUTE,
        renderer="/supply/supplier_order.mako",
        permission=PERMISSIONS["company.view"],
        layout="opa",
    )

    config.add_view(
        SupplierOrderDeleteView,
        route_name=ITEM_ROUTE,
        request_param="action=delete",
        permission=PERMISSIONS["context.delete_supplier_order"],
        request_method="POST",
        require_csrf=True,
    )

    config.add_view(
        SupplierOrderDuplicateView,
        route_name=ITEM_ROUTE,
        request_param="action=duplicate",
        permission=PERMISSIONS["context.duplicate_supplier_order"],
        request_method="POST",
        require_csrf=True,
    )

    # File attachment
    config.add_view(
        FileUploadView,
        route_name=f"{ITEM_ROUTE}/addfile",
        renderer="base/formpage.mako",
        permission=PERMISSIONS["context.add_file"],
    )

    config.add_admin_menu(
        parent="sale",
        order=3,
        label="Commandes fournisseurs",
        href=COLLECTION_ROUTE,
        routes_prefixes=[ITEM_ROUTE],
        permission=PERMISSIONS["global.list_supplier_orders"],
    )
    config.add_company_menu(
        parent="supply",
        order=1,
        label="Commandes fournisseurs",
        route_name=COMPANY_COLLECTION_ROUTE,
        route_id_key="company_id",
        routes_prefixes=[ITEM_ROUTE],
    )

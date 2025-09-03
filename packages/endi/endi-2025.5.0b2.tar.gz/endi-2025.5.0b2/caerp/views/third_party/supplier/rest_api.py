from caerp.consts.permissions import PERMISSIONS
from caerp.forms.third_party.supplier import (
    get_edit_internal_supplier_schema,
    get_supplier_schema,
    get_add_edit_supplier_schema,
)
from caerp.models.company import Company
from caerp.models.status import StatusLogEntry
from caerp.models.third_party import Supplier
from caerp.views import BaseRestView
from caerp.views.status.rest_api import StatusLogEntryRestView
from caerp.views.status.utils import get_visibility_options
from caerp.views.third_party.supplier.routes import (
    COMPANY_SUPPLIERS_API_ROUTE,
    SUPPLIER_ITEM_API_ROUTE,
    SUPPLIER_ITEM_STATUSLOGENTRY_API_ROUTE,
    SUPPLIER_STATUSLOGENTRY_ITEM_API_ROUTE,
)


class SupplierRestView(BaseRestView):
    """
    Supplier rest view

    collection : context Root

        GET : return list of suppliers (company_id should be provided)
    """

    def get_schema(self, submitted):
        if isinstance(self.context, Supplier):
            if self.context.is_internal():
                schema = get_edit_internal_supplier_schema()
            else:
                # Aucune idée comment on arrive ici mais on conserve ce
                # fonctionnement
                if "formid" in submitted:
                    schema = get_supplier_schema()
        else:
            if "formid" in submitted:
                schema = get_supplier_schema()
            else:
                excludes = ("company_id",)
                schema = get_add_edit_supplier_schema(excludes=excludes)
        return schema

    def collection_get(self):
        return self.context.suppliers

    def post_format(self, entry, edit, attributes):
        """
        Associate a newly created element to the parent company
        """
        if not edit:
            entry.company = self.context
        return entry

    def form_config(self):
        return {"options": {"visibilities": get_visibility_options(self.request)}}


def includeme(config):
    config.add_rest_service(
        SupplierRestView,
        SUPPLIER_ITEM_API_ROUTE,
        collection_route_name=COMPANY_SUPPLIERS_API_ROUTE,
        collection_context=Company,
        context=Supplier,
        collection_view_rights=PERMISSIONS["company.view"],
        view_rights=PERMISSIONS["company.view"],
        edit_rights=PERMISSIONS["context.edit_supplier"],
        add_rights=PERMISSIONS["context.add_supplier"],
        delete_rights=PERMISSIONS["context.delete_supplier"],
    )
    config.add_view(
        SupplierRestView,
        attr="form_config",
        route_name=SUPPLIER_ITEM_API_ROUTE,
        renderer="json",
        request_param="form_config",
        permission=PERMISSIONS["context.edit_supplier"],
        context=Supplier,
    )
    config.add_rest_service(
        StatusLogEntryRestView,
        SUPPLIER_STATUSLOGENTRY_ITEM_API_ROUTE,
        collection_route_name=SUPPLIER_ITEM_STATUSLOGENTRY_API_ROUTE,
        collection_view_rights=PERMISSIONS["company.view"],
        context=StatusLogEntry,
        add_rights=PERMISSIONS["company.view"],
        view_rights=PERMISSIONS["context.view_statuslogentry"],
        edit_rights=PERMISSIONS["context.edit_statuslogentry"],
        delete_rights=PERMISSIONS["context.delete_statuslogentry"],
    )

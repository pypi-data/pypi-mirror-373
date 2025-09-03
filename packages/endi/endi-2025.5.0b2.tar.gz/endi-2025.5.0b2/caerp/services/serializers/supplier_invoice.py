"""
Supplier invoice serializers used for supplier invoice related views
"""

from caerp.compute.math_utils import integer_to_amount
from caerp.consts.permissions import PERMISSIONS
from caerp.services.serializers.base import BaseSerializer


class SupplierInvoiceSerializer(BaseSerializer):
    acl = {
        "__all__": PERMISSIONS["global.manage_accounting"],
        "supplier": PERMISSIONS["global.manage_accounting"],
        "company": PERMISSIONS["global.manage_accounting"],
        "payer": PERMISSIONS["global.manage_accounting"],
    }
    exclude_from_children = (
        "node",
        "supplier_invoice",
        "supplier_invoices",
    )

    def get_total_label(self, request, item, field_name):
        value = item.total
        return integer_to_amount(value)

    def get_label(self, request, item, field_name):
        if item:
            return f"N° {item.official_number} du {item.date.strftime('%d/%m/%Y')}"

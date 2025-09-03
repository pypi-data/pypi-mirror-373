"""
Sepa serializers used for the SEPA related views

.. code-block:: command

    In [1]: from pyramid.security import remember

    In [2]: from caerp.services.serializers import serializers

    In [3]: from caerp.models.sepa import BaseSepaWaitingPayment

    In [4]: from caerp.utils.rest.apiv1 import FieldOptions

    In [5]: remember(request, 'admin.majerti')
    Out[5]: []

    In [6]: waiting = BaseSepaWaitingPayment.query().all()[0]

    In [8]: fields = FieldOptions(attributes=['id', 'amount', 'node_id'], relationships_dict={'expense_sheet': {'attributes': ['id', 'date_label', 'official_number'], 'relationships': {'user': {'attributes': ['id', 'label', 'has_bank_account']}}}, 'supplier_invoice': {'attributes': ['id', 'date_label', 'official_number'], 'relationships': {'supplier': {'attributes': ['id', 'label', 'has_ban_account']}}}})

    In [9]: serializer = serializers['sepa_waiting_payment'](fields, serializers)

    In [10]: serializer.run(request, waiting)
    {'id': 1,
    'amount': 151760,
    'node_id': 608817,
    'expense_sheet': {'id': 608817,
    'date_label': None,
    'official_number': '2025-152029',
    'user': {'id': 72, 'label': 'MIRAMBEAU Mandine', 'has_bank_account': False}},
    'supplier_invoice': {'id': None,
    'date_label': None,
    'official_number': None,
    'supplier': {'id': None, 'label': None, 'has_ban_account': None}}}


"""


from caerp.compute.math_utils import integer_to_amount
from caerp.consts.permissions import PERMISSIONS
from caerp.services.serializers.base import BaseSerializer


class SepaCreditTransferSerializer(BaseSerializer):
    acl = {
        "__all__": PERMISSIONS["global.manage_accounting"],
        "sepa_waiting_payments": PERMISSIONS["global.manage_accounting"],
        "bank_account": PERMISSIONS["global.manage_accounting"],
        "user": PERMISSIONS["global.manage_accounting"],
    }
    exclude_from_children = ("sepa_credit_transfer",)

    def get_amount(self, request, item, value):
        value = sum(payment.amount for payment in item.sepa_waiting_payments)
        return value


class SepaWaitingSerializer(BaseSerializer):
    acl = {
        "__all__": PERMISSIONS["global.manage_accounting"],
        "expense_sheet": PERMISSIONS["global.manage_accounting"],
        "supplier_invoice": PERMISSIONS["global.manage_accounting"],
    }
    exclude_from_children = ("sepa_waiting_payments",)

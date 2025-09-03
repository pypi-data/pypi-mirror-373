import functools


from caerp.views.supply.orders.views import stream_supplier_order_actions


class SupplierOrderListPanel:
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(
        self,
        records,
        stream_actions=None,
        is_admin_view=False,
        is_supplier_view=False,
    ):
        stream_actions = functools.partial(
            stream_supplier_order_actions,
            self.request,
        )

        return dict(
            records=records,
            is_admin_view=is_admin_view,
            is_supplier_view=is_supplier_view,
            stream_actions=stream_actions,
        )


def includeme(config):
    config.add_panel(
        SupplierOrderListPanel,
        "supplier_order_list",
        renderer="panels/supply/supplier_order_list.mako",
    )

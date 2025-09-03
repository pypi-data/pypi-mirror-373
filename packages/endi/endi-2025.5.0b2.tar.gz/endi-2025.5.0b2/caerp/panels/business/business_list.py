from caerp.utils.widgets import Link
from caerp.views.business.routes import BUSINESS_ITEM_ROUTE


class BusinessListPanel:
    def __init__(self, context, request):
        self.context = context
        self.request = request

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

    def __call__(
        self,
        records,
        is_admin_view=True,
        is_customer_view=False,
    ):
        ret_dict = dict(
            records=records,
            is_admin_view=is_admin_view,
            is_customer_view=is_customer_view,
            nb_columns=9,
            total_colspan=4,
        )
        if is_admin_view:
            ret_dict["nb_columns"] += 1
            ret_dict["total_colspan"] += 1
        if is_customer_view:
            ret_dict["nb_columns"] -= 1
            ret_dict["total_colspan"] -= 1
        ret_dict["total_estimated"] = sum(
            r.get_total_estimated("ttc") for id_, r in records
        )
        ret_dict["total_invoiced"] = sum(
            r.get_total_income("ttc") for id_, r in records
        )
        ret_dict["total_to_invoice"] = sum(
            r.amount_to_invoice("ttc") for id_, r in records
        )
        ret_dict["total_to_pay"] = sum(r.get_topay() for id_, r in records)
        ret_dict["stream_actions"] = self.stream_actions
        return ret_dict


def includeme(config):
    config.add_panel(
        BusinessListPanel,
        "business_list",
        renderer="panels/business/business_list.mako",
    )

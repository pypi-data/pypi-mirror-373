from caerp.consts.permissions import PERMISSIONS
from caerp.models.third_party.customer import Customer
from caerp.forms.business.business import get_business_list_schema
from caerp.views import TreeMixin
from caerp.views.business.lists import GlobalBusinessListView
from caerp.views.third_party.customer.lists import CustomersListView

from .routes import CUSTOMER_ITEM_BUSINESS_ROUTE


class CustomerBusinessListView(GlobalBusinessListView, TreeMixin):
    is_admin = False
    is_customer_list = True
    route_name = CUSTOMER_ITEM_BUSINESS_ROUTE
    add_template_vars = GlobalBusinessListView.add_template_vars + ("is_customer_list",)

    def get_schema(self):
        return get_business_list_schema(
            self.request, is_global=False, is_customer_list=True
        )

    @property
    def title(self):
        return "Affaires du client {0}".format(self.context.label)

    def filter_company_customer(self, query, appstruct):
        appstruct["company_id"] = self.context.company.id
        appstruct["customer_id"] = self.context.id
        return query


def includeme(config):
    config.add_tree_view(
        CustomerBusinessListView,
        parent=CustomersListView,
        renderer="customers/businesses.mako",
        permission=PERMISSIONS["company.view"],
        layout="customer",
        context=Customer,
    )

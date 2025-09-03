from caerp.consts.permissions import PERMISSIONS
from caerp.models.third_party import Customer
from caerp.views import BaseView, TreeMixin
from caerp.views.project.project import ProjectEntryPointView
from caerp.views.third_party.customer.routes import CUSTOMER_ITEM_EXPENSES_ROUTE


class CustomerLinkedExpensesView(BaseView, TreeMixin):

    route_name = CUSTOMER_ITEM_EXPENSES_ROUTE
    add_template_vars = ("title",)

    @property
    def title(self):
        customer = self.context
        return "Achats liés au client {}".format(customer.label)

    def __call__(self):
        self.populate_navigation()
        return dict(title=self.title)


def includeme(config):
    config.add_tree_view(
        CustomerLinkedExpensesView,
        parent=ProjectEntryPointView,
        renderer="caerp:templates/customers/expenses.mako",
        permission=PERMISSIONS["company.view"],
        layout="customer",
        context=Customer,
    )

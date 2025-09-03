from caerp.compute.sale_product import SaleProductHtComputer


class ProductHtComputer(SaleProductHtComputer):
    def _get_company(self):
        return self.product.get_company()


class WorkItemHtComputer(ProductHtComputer):
    def _get_tva(self):
        return self.product.get_tva()

    def work_unit_flat_cost(self):
        return 0

    def full_flat_cost(self):
        return 0

    def full_cost_price(self):
        return 0

    def full_intermediate_price(self):
        return 0

    def full_price_with_contribution(self, base_price=None):
        return 0

    def full_price_with_insurance(self, base_price=None):
        return 0

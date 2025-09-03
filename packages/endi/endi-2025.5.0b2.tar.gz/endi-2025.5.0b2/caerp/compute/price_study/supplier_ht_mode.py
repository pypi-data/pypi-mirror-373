from caerp.compute.sale_product import SaleProductSupplierHtComputer


class ProductSupplierHtComputer(SaleProductSupplierHtComputer):
    def __init__(self, product, config):
        super().__init__(product, config)
        self.task = product.get_task()
        self.prefix = ""
        if self.task is not None:
            self.prefix = self.task.prefix

    def _get_contribution(self):
        from caerp.models.company import Company

        return Company.get_contribution(self.company.id, prefix=self.prefix)

    def _get_insurance(self):
        if self.task:
            return self.task.get_rate("insurance")
        else:
            from caerp.models.company import Company

            return Company.get_rate(self.company.id, "insurance", prefix=self.prefix)

    def _get_company(self):
        return self.product.get_company()

    def get_general_overhead(self):
        return self.product.get_general_overhead()

    def get_margin_rate(self):
        return self.product.margin_rate


class WorkItemSupplierHtComputer(ProductSupplierHtComputer):
    def get_margin_rate(self):
        return self.product.get_margin_rate()

    def _get_tva(self):
        return self.product.get_tva()

    def work_unit_flat_cost(self):
        value = self.flat_cost()
        quantity = self.product.work_unit_quantity
        if quantity is None:
            quantity = 0
        return quantity * value

    def _get_quantity(self):
        quantity = self.product.total_quantity
        if quantity is None:
            quantity = 0
        return quantity

    def full_flat_cost(self):
        value = self.flat_cost()
        return value * self._get_quantity()

    def full_cost_price(self):
        value = self.cost_price()
        return value * self._get_quantity()

    def full_intermediate_price(self):
        value = self.intermediate_price()
        return value * self._get_quantity()

    def full_price_with_contribution(self, base_price=None):
        value = self.price_with_contribution(base_price)
        if base_price:
            return value
        else:
            return value * self._get_quantity()

    def full_price_with_insurance(self, base_price=None):
        value = self.price_with_insurance(base_price)
        if base_price:
            return value
        else:
            return value * self._get_quantity()

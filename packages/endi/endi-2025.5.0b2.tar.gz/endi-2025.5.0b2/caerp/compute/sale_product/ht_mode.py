from caerp.compute.math_utils import compute_tva


class SaleProductHtComputer:
    def __init__(self, product, config):
        self.product = product
        self.company = self._get_company()
        self.tva = self._get_tva()

    def _get_company(self):
        return self.product.company

    def _get_tva(self):
        return self.product.tva

    def flat_cost(self):
        return 0

    def cost_price(self):
        return 0

    def intermediate_price(self):
        return 0

    def price_with_contribution(self, base_price=None):
        return 0

    def price_with_insurance(self, base_price=None):
        return 0

    def unit_ht(self):
        return self.product.ht or 0

    def unit_ttc(self):
        """
        Compute the ttc value for the given sale product
        """
        ht = self.unit_ht()
        tva = self.tva
        if tva is not None:
            return ht + compute_tva(ht, tva.value)
        else:
            return ht


class SaleProductWorkItemHtComputer(SaleProductHtComputer):
    def _get_company(self):
        return self.product.get_company()

    def _get_tva(self):
        return self.product.get_tva()

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

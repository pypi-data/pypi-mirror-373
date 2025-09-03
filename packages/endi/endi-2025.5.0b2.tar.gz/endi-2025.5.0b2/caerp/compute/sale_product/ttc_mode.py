from caerp.compute.math_utils import compute_ht_from_ttc


class SaleProductTtcComputer:
    """
    Computer used in ttc mode
    """

    def __init__(self, product, config):
        self.product = product
        self.tva = self._get_tva()

    def _get_tva(self):
        return self.product.tva

    def unit_ht(self, contribution=None):
        ttc = self.unit_ttc()
        tva_object = self.tva
        if tva_object is not None:
            return compute_ht_from_ttc(
                ttc,
                tva_object.value,
                float_format=False,
            )
        else:
            return ttc

    def unit_ttc(self):
        """
        Compute the ttc value for the given sale product
        """
        return self.product.ttc or 0

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

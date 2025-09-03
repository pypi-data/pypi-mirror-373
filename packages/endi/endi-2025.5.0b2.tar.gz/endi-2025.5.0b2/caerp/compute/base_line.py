class BaseLineCompute:
    """
    Common class for basic lines compute

    Attributs utilisés pour le calcul
    self.ht (float)
    self.tva (float)
    """

    @property
    def total(self):
        return self.total_ht + self.total_tva

    @property
    def total_ht(self):
        return self.ht

    @property
    def total_tva(self):
        return self.tva

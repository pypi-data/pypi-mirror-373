class BaseGeneUpdater:
    """
    Base class for variable update
    """

    def __init__(self):
        self.population = None

    def update_genes(self, population):
        self.population = population
        self._update_genes()

    def _update_genes(self):
        pass

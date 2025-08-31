import math

from gadapt.operations.population_update.base_population_updater import (
    BasePopulationUpdater,
)
from gadapt.utils import ga_utils


class CostDiversityPopulationUpdater(BasePopulationUpdater):
    """
    Common population updater
    """

    def _calculate_absolute_cost_diversity(self):
        allocated_values = [
            c.cost_value
            for c in self.population.chromosomes
            if c.cost_value is not None and not math.isnan(c.cost_value)
        ]
        if allocated_values:
            return ga_utils.average_difference(allocated_values)
        return float("NaN")

    def _update_population(self):
        self.population.absolute_cost_diversity = (
            self._calculate_absolute_cost_diversity()
        )
        if math.isnan(self.population.absolute_cost_diversity_in_first_population):
            self.population.absolute_cost_diversity_in_first_population = (
                self.population.absolute_cost_diversity
            )

from typing import List

from gadapt.ga_model.chromosome import Chromosome
from gadapt.operations.immigration.population_immigration.base_population_immigrator import (
    BasePopulationImmigrator,
)


class CommonPopulationImmigrator(BasePopulationImmigrator):
    """
    Common class for the self.population immigration.
    In kept part of the self.population lower ranked chromosomes are replaced with new ones
    """

    def _immigrate_population(self):
        if self.population.options.immigration_number < 1:
            return
        keep_number = self.population.options.keep_number
        chromosome_list: List[Chromosome] = list(
            self.population.get_sorted(key=lambda c: c.cost_value)
        )[:keep_number]
        chromosome_list = sorted(
            chromosome_list, key=lambda c: (-c.cost_value, -c.chromosome_id)
        )[: self.population.options.immigration_number]
        for c in chromosome_list:
            self._chromosome_immigrator.immigrate(c)
            c.population_generation = self.population.population_generation

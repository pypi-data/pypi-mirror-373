import math
from typing import List

from gadapt.adapters.ga_logging.logging_settings import gadapt_log_info
from gadapt.ga_model.chromosome import Chromosome
from gadapt.operations.cost_finding.base_cost_finder import BaseCostFinder


class ElitismCostFinder(BaseCostFinder):
    """
    Finding costs for a better half of the population
    """

    def _find_costs_for_population(self):
        if self.population is None:
            raise Exception("population must not be null!")
        chromosomes_for_execution: List[Chromosome] = [
            c
            for c in self.population
            if (math.isnan(c.cost_value))
            or (
                c.is_immigrant
                and c.population_generation == self.population.population_generation
            )
        ]
        for c in chromosomes_for_execution:
            self._execute_function(self.population.options.cost_function, c)
        better_chromosomes: List[Chromosome] = self.population.get_sorted(
            key=lambda x: x.cost_value
        )[: self.population.options.keep_number]
        self.population.best_individual = better_chromosomes[0]
        self.population.min_cost = (
            min(better_chromosomes, key=lambda x: x.cost_value)
        ).cost_value
        better_chromosomes_without_immigrants = better_chromosomes[
            : self.population.options.keep_number
            - self.population.options.immigration_number
        ]
        self.population.avg_cost = sum(
            [c.cost_value for c in better_chromosomes_without_immigrants]
        ) / len(better_chromosomes_without_immigrants)
        self._log_population()
        self.population.clear_and_add_chromosomes(better_chromosomes)

    def _log_population(self):
        if self.population.options.logging:
            gadapt_log_info(str(self.population))

import math

from gadapt.adapters.ga_logging.logging_settings import gadapt_log_error
from gadapt.operations.mutation.population_mutation.base_chromosome_mutation_rate_determinator import (
    BaseChromosomeMutationRateDeterminator,
)


class CostDiversityChromosomeMutationRateDeterminator(
    BaseChromosomeMutationRateDeterminator
):
    """
    Determines the number of chromosomes to be mutated in a population based on the cost diversity of the population.
    """

    def __init__(
        self,
    ) -> None:
        super().__init__()

    def _get_cost_diversity_coefficient(self):
        cost_diversity_coefficient = float(
            self.population.absolute_cost_diversity
            / self.population.absolute_cost_diversity_in_first_population
        )
        if cost_diversity_coefficient > 1.0:
            cost_diversity_coefficient = 1.0
        return cost_diversity_coefficient

    def _get_mutation_rate(self) -> float:
        if (
            self.population.absolute_cost_diversity_in_first_population is None
            or math.isnan(self.population.absolute_cost_diversity_in_first_population)
            or self.population.absolute_cost_diversity is None
            or math.isnan(self.population.absolute_cost_diversity)
        ):
            gadapt_log_error("absolute_cost_diversity not set!")
            return 1.0
        return 1.0 - self._get_cost_diversity_coefficient()

    def _get_number_of_mutation_chromosomes(self) -> int:

        mutation_rate = self._get_mutation_rate()
        f_return_value = mutation_rate * float(self.max_number_of_mutation_chromosomes)
        return round(f_return_value)

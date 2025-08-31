import gadapt.utils.ga_utils as ga_utils
from gadapt.operations.mutation.population_mutation.base_chromosome_mutation_rate_determinator import (
    BaseChromosomeMutationRateDeterminator,
)


class CrossDiversityChromosomeMutationRateDeterminator(
    BaseChromosomeMutationRateDeterminator
):
    """
    Determining the number of chromosomes to be mutated in a population based on the cross-diversity coefficient of the genes.
    """

    def __init__(
        self,
    ) -> None:
        super().__init__()

    def _get_number_of_mutation_chromosomes(self) -> int:
        def get_mutation_rate() -> float:
            avg_rsd = ga_utils.average(
                [g.cross_diversity_coefficient for g in self.population.options.genes]
            )
            if avg_rsd > 1:
                avg_rsd = 1
            if avg_rsd < 0:
                avg_rsd = 0
            return 1 - avg_rsd

        mutation_rate = get_mutation_rate()
        f_return_value = mutation_rate * float(self.max_number_of_mutation_chromosomes)
        return round(f_return_value)

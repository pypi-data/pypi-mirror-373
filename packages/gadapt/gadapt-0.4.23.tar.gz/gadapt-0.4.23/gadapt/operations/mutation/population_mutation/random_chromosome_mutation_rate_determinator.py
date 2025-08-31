import random

from gadapt.operations.mutation.population_mutation.base_chromosome_mutation_rate_determinator import (
    BaseChromosomeMutationRateDeterminator,
)


class RandomChromosomeMutationRateDeterminator(BaseChromosomeMutationRateDeterminator):
    """
    Provides a random method for determining the number of chromosomes to be mutated in a population.
    """

    def __init__(
        self,
    ) -> None:
        super().__init__()

    def _get_number_of_mutation_chromosomes(self) -> int:
        return random.randint(1, self.max_number_of_mutation_chromosomes)

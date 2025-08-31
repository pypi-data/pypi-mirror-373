import random

from gadapt.ga_model.chromosome import Chromosome
from gadapt.operations.mutation.population_mutation.base_chromosome_mutation_rate_determinator import (
    BaseChromosomeMutationRateDeterminator,
)
from gadapt.operations.mutation.population_mutation.base_chromosome_mutation_selector import (
    BaseChromosomeMutationSelector,
)
from gadapt.operations.mutation.chromosome_mutation.base_gene_mutation_selector import (
    BaseGeneMutationSelector,
)


class RandomChromosomeMutationSelector(BaseChromosomeMutationSelector):
    """
    Implements the mutation of chromosomes in a population based on a random selection of chromosomes
    """

    def __init__(
        self,
        chromosome_mutation_rate_determinator: BaseChromosomeMutationRateDeterminator,
        gene_mutation_selector: BaseGeneMutationSelector,
    ) -> None:
        super().__init__(chromosome_mutation_rate_determinator, gene_mutation_selector)

    def _mutate_population(self):
        if self.population is None:
            raise Exception("population must not be None")
        unallocated_chromosomes = self._get_unallocated_chromosomes(
            self._sort_key_random
        )
        mutation_chromosome_number = self.number_of_mutation_chromosomes
        if mutation_chromosome_number == 0:
            return 0
        chromosomes_for_mutation = unallocated_chromosomes[:mutation_chromosome_number]
        for c in chromosomes_for_mutation:
            self._gene_mutation_selector.mutate(
                c, self.population.options.number_of_mutation_genes
            )
        return mutation_chromosome_number

    def _sort_key_random(self, _: Chromosome):
        return random.random()

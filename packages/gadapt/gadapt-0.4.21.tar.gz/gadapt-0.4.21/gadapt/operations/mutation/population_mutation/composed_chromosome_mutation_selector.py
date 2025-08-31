import random
from typing import List

from gadapt.operations.mutation.population_mutation.base_chromosome_mutation_rate_determinator import (
    BaseChromosomeMutationRateDeterminator,
)
from gadapt.operations.mutation.population_mutation.base_chromosome_mutation_selector import (
    BaseChromosomeMutationSelector,
)
from gadapt.operations.mutation.chromosome_mutation.base_gene_mutation_selector import (
    BaseGeneMutationSelector,
)


class ComposedChromosomeMutationSelector(BaseChromosomeMutationSelector):
    def __init__(
        self,
        chromosome_mutation_rate_determinator: BaseChromosomeMutationRateDeterminator,
        gene_mutation_selector: BaseGeneMutationSelector,
    ) -> None:
        super().__init__(chromosome_mutation_rate_determinator, gene_mutation_selector)
        self.selectors: List[BaseChromosomeMutationSelector] = []

    def append(self, selector: BaseChromosomeMutationSelector):
        """
        Appends selector to the composition of selectors
        """
        self.selectors.append(selector)

    def _mutate_population(self):
        if self.population is None:
            raise Exception("Population must not be null")
        if len(self.selectors) == 0:
            raise Exception("at least one mutator must be added")
        if len(self.selectors) > 1:
            random.shuffle(self.selectors)
        nmc = 0
        limit_number_of_mutation_chromosomes = self.number_of_mutation_chromosomes
        if limit_number_of_mutation_chromosomes == 0:
            return 0
        for m in self.selectors:
            if nmc < limit_number_of_mutation_chromosomes:
                m.population = self.population
                m.number_of_mutation_chromosomes = (
                    limit_number_of_mutation_chromosomes - nmc
                )
                mc = m._mutate_population()
                nmc += mc
        return nmc

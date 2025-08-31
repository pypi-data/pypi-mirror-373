import math
from abc import ABC, abstractmethod
from typing import List

from gadapt.ga_model.chromosome import Chromosome
from gadapt.operations.mutation.population_mutation.base_chromosome_mutation_rate_determinator import (
    BaseChromosomeMutationRateDeterminator,
)
from gadapt.operations.mutation.chromosome_mutation.base_gene_mutation_selector import (
    BaseGeneMutationSelector,
)


class BaseChromosomeMutationSelector(ABC):
    """
    Selects and mutates the chromosomes in the population based on a specified number of mutated chromosomes.
    """

    def __init__(
        self,
        chromosome_mutation_rate_determinator: BaseChromosomeMutationRateDeterminator,
        gene_mutation_selector: BaseGeneMutationSelector,
    ) -> None:
        """
        Base class for selecting mating chromosomes in population
        Args:
            chromosome_mutation_rate_determinator: chromosome mutation rate determinator
        """
        super().__init__()
        self._chromosome_mutation_rate_determinator = (
            chromosome_mutation_rate_determinator
        )
        self.number_of_mutation_chromosomes = -1
        self._gene_mutation_selector = gene_mutation_selector

    def mutate(self, population):
        """
        Mutates chromosomes in the population
        Args:
            population: Population to mutate
        """
        self.population = population
        max_number_of_mutated_chromosomes = (
            population.options.number_of_mutation_chromosomes
        )
        self.number_of_mutation_chromosomes = self._chromosome_mutation_rate_determinator.get_number_of_mutation_chromosomes(
            self.population, max_number_of_mutated_chromosomes
        )
        self._mutate_population()

    @abstractmethod
    def _mutate_population(self):
        pass

    def mutate_chromosome(self, c: Chromosome, number_of_mutated_chromosomes: int):
        self._gene_mutation_selector.mutate(c, number_of_mutated_chromosomes)

    def _get_unallocated_chromosomes(self, sort_key_function=None) -> List[Chromosome]:
        def unallocated_chromosomes_condition(c: Chromosome) -> bool:
            return (
                math.isnan(c.cost_value)
                and (not c.is_immigrant)
                and c.population_generation == self.population.population_generation
                and not c.is_mutated
            )

        lst = [c for c in self.population if (unallocated_chromosomes_condition(c))]
        if sort_key_function is not None:
            lst.sort(key=sort_key_function)
        return lst

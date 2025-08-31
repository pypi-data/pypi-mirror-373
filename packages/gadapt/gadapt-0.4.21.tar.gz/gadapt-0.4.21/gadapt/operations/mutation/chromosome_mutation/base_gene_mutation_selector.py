from abc import ABC, abstractmethod

from gadapt.ga_model.allele import Allele
from gadapt.operations.mutation.chromosome_mutation.base_gene_mutation_rate_determinator import (
    BaseGeneMutationRateDeterminator,
)
from gadapt.operations.mutation.gene_mutation.base_gene_mutator import BaseGeneMutator


class BaseGeneMutationSelector(ABC):
    """
    Provides a framework for selecting and mutating genes in a chromosome.
    """

    def __init__(
        self,
        gene_mutation_rate_determinator: BaseGeneMutationRateDeterminator,
        gene_mutator: BaseGeneMutator,
    ):
        """
        Initializes an instance of the class by setting the gene_mutation_rate_determinator attribute.
        """
        self.chromosome = None
        self._gene_mutation_rate_determinator = gene_mutation_rate_determinator
        self._gene_mutator = gene_mutator
        self.number_of_mutation_genes = -1

    def mutate(self, c, number_of_mutation_genes: int):
        """
        Selects and mutates genes in the chromosome
        Args:
            c: Chromosome to mutate
            number_of_mutation_genes: Number of mutation genes
        """
        self.chromosome = c
        self.number_of_mutation_genes = number_of_mutation_genes
        self._before_mutated()
        self._mutate_chromosome()
        self._chromosome_mutated()

    @abstractmethod
    def _mutate_chromosome(self):
        pass

    def _mutate_gene(self, g: Allele):
        self._gene_mutator.mutate(g)
        self._gene_mutated(g)

    def _gene_mutated(self, g):
        self.chromosome.mutated_variables_id_list.append(g.gene.variable_id)

    def _chromosome_mutated(self):
        self.chromosome.is_mutated = True
        if self.chromosome.first_mutant_generation == 0:
            self.chromosome.first_mutant_generation += 1
        self.chromosome.last_mutant_generation = 1

    def _before_mutated(self):
        self.chromosome.mutated_variables_id_list.clear()

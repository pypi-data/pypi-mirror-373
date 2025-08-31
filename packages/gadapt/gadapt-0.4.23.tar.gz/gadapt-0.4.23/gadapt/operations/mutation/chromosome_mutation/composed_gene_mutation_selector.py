import random
from typing import List

from gadapt.operations.mutation.chromosome_mutation.base_gene_mutation_rate_determinator import (
    BaseGeneMutationRateDeterminator,
)
from gadapt.operations.mutation.chromosome_mutation.base_gene_mutation_selector import (
    BaseGeneMutationSelector,
)
from gadapt.operations.mutation.gene_mutation.base_gene_mutator import BaseGeneMutator


class ComposedGeneMutationSelector(BaseGeneMutationSelector):
    """
    Allows for the composition of multiple mutation selectors and applies them sequentially to the chromosome.
    """

    def __init__(
        self,
        gene_mutation_rate_determinator: BaseGeneMutationRateDeterminator,
        gene_mutator: BaseGeneMutator,
    ) -> None:
        super().__init__(gene_mutation_rate_determinator, gene_mutator)
        self.selectors: List[BaseGeneMutationSelector] = []

    def append(self, selector: BaseGeneMutationSelector):
        """
        Appends mutation selectors to a list of selectors.
        Args:
            selector: An instance of the BaseGeneMutationSelector class that will be added to the list of selectors.
        """
        self.selectors.append(selector)

    def _mutate_chromosome(self):
        if self.chromosome is None:
            raise Exception("Chromosome must not be null")
        if len(self.selectors) == 0:
            raise Exception("at least one mutator must be added")
        if len(self.selectors) > 1:
            random.shuffle(self.selectors)
        nmg = 0
        number_of_mutation_genes = (
            self._gene_mutation_rate_determinator.get_number_of_mutation_genes(
                self.chromosome, self.number_of_mutation_genes
            )
        )
        if number_of_mutation_genes == 0:
            number_of_mutation_genes = 1
        for s in self.selectors:
            if nmg < number_of_mutation_genes:
                s.number_of_mutation_genes = number_of_mutation_genes - nmg
                s.chromosome = self.chromosome
                mg = s._mutate_chromosome()
                nmg += mg
        return nmg

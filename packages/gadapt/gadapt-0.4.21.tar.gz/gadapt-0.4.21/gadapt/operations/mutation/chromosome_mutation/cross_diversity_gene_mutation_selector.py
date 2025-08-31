import random

from gadapt.operations.mutation.chromosome_mutation.base_gene_mutation_rate_determinator import (
    BaseGeneMutationRateDeterminator,
)
from gadapt.operations.mutation.chromosome_mutation.random_gene_mutation_selector import (
    RandomGeneMutationSelector,
)
from gadapt.operations.sampling.base_sampling import BaseSampling
from gadapt.operations.mutation.gene_mutation.base_gene_mutator import BaseGeneMutator


class CrossDiversityGeneMutationSelector(RandomGeneMutationSelector):
    """
    Selects and mutates a chromosome based on the cross diversity of genes in the population.
    """

    def __init__(
        self,
        gene_mutation_rate_determinator: BaseGeneMutationRateDeterminator,
        gene_mutator: BaseGeneMutator,
        sampling: BaseSampling,
    ) -> None:
        super().__init__(gene_mutation_rate_determinator, gene_mutator)
        self._sampling = sampling

    def _mutate_chromosome(self):
        if self.number_of_mutation_genes == 0:
            self.number_of_mutation_genes = 1
        x_genes = [g for g in self.chromosome]
        x_genes.sort(key=lambda g: -g.gene.cross_diversity_coefficient)
        number_of_mutation_genes = (
            self._gene_mutation_rate_determinator.get_number_of_mutation_genes(
                self.chromosome, self.number_of_mutation_genes
            )
        )
        if number_of_mutation_genes > len(x_genes):
            number_of_mutation_genes = len(x_genes)
        if number_of_mutation_genes == 0:
            max_number_of_mutation_genes = 1
        else:
            max_number_of_mutation_genes = random.randint(1, number_of_mutation_genes)
        genes_for_mutation = self._sampling.get_sample(
            x_genes,
            max_number_of_mutation_genes,
            lambda g: g.gene.cross_diversity_coefficient,
        )
        for g in genes_for_mutation:
            self._mutate_gene(g)
        return len(genes_for_mutation)

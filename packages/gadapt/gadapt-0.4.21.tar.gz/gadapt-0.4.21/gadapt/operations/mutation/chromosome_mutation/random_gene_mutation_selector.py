import random

from gadapt.operations.mutation.chromosome_mutation.base_gene_mutation_rate_determinator import (
    BaseGeneMutationRateDeterminator,
)
from gadapt.operations.mutation.chromosome_mutation.base_gene_mutation_selector import (
    BaseGeneMutationSelector,
)
from gadapt.operations.mutation.gene_mutation.base_gene_mutator import BaseGeneMutator


class RandomGeneMutationSelector(BaseGeneMutationSelector):
    """
    Selects and mutates genes in a chromosome using a random mutation strategy.
    """

    def __init__(
        self,
        gene_mutation_rate_determinator: BaseGeneMutationRateDeterminator,
        gene_mutator: BaseGeneMutator,
    ):
        super().__init__(gene_mutation_rate_determinator, gene_mutator)

    def _mutate_chromosome(self):
        if self.number_of_mutation_genes < 1:
            self.number_of_mutation_genes = 1
        genes_to_mutate = list(self.chromosome)
        random.shuffle(genes_to_mutate)
        number_of_mutation_genes = (
            self._gene_mutation_rate_determinator.get_number_of_mutation_genes(
                self.chromosome, self.number_of_mutation_genes
            )
        )
        if number_of_mutation_genes < 1:
            number_of_mutation_genes = 1
        var_num = random.randint(1, number_of_mutation_genes)
        for g in genes_to_mutate[:var_num]:
            self._mutate_gene(g)

        return var_num

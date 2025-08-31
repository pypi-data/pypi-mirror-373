import random

from gadapt.operations.mutation.chromosome_mutation.base_gene_mutation_rate_determinator import (
    BaseGeneMutationRateDeterminator,
)


class RandomGeneMutationRateDeterminator(BaseGeneMutationRateDeterminator):
    """
    Determines the random number of mutation genes in a chromosome between 1 and the maximum number of mutation genes specified.
    """

    def __init__(
        self,
    ) -> None:
        super().__init__()

    def _get_number_of_mutation_genes(self) -> int:
        return random.randint(1, self.max_number_of_mutation_genes)

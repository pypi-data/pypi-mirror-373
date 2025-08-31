from gadapt.operations.mutation.gene_mutation.base_gene_mutator import BaseGeneMutator


class RandomGeneMutator(BaseGeneMutator):
    """
    Generates a random value within the specified range of the gene.
    """

    def _make_mutated_value(self):
        return round(
            self.gene_value.gene.make_random_value(),
            self.gene_value.gene.decimal_places,
        )

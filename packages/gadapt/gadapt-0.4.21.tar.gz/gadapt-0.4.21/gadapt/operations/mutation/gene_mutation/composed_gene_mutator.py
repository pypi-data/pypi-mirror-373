import random
from typing import List

from gadapt.operations.mutation.gene_mutation.base_gene_mutator import BaseGeneMutator


class ComposedGeneMutator(BaseGeneMutator):
    def __init__(self) -> None:
        super().__init__()
        self.mutators: List[BaseGeneMutator] = []

    def append(self, mutator: BaseGeneMutator):
        """
        Appends gene mutator to a list of mutators.
        Args:
            mutator: An instance of the BaseGeneMutator class that will be added to the list of mutator.
        """
        self.mutators.append(mutator)

    def _make_mutated_value(self):
        if self.gene_value is None:
            raise Exception("Allele must not be null")
        if len(self.mutators) == 0:
            raise Exception("at least one mutator must be added")
        for mutator in self.mutators:
            mutator.gene_value = self.gene_value
        if len(self.mutators) > 1:
            random.shuffle(self.mutators)
        return self.mutators[0]._make_mutated_value()

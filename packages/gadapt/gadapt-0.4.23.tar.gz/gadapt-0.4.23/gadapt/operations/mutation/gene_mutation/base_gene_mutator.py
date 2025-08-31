from abc import ABC, abstractmethod

from gadapt.ga_model.allele import Allele


class BaseGeneMutator(ABC):
    """
    Mutates the variable value of a gene.
    """

    def mutate(self, gene_value: Allele):
        self.gene_value = gene_value
        self.gene_value.variable_value = self._make_mutated_value()

    @abstractmethod
    def _make_mutated_value(self):
        pass

    def _execute_function_until_value_changed(self, f):
        current_gene_value = self.gene_value.variable_value
        number_of_attempts = 5
        i = 0
        while True:
            new_gene_value = f()
            i += 1
            if new_gene_value != current_gene_value or i >= number_of_attempts:
                break
        return new_gene_value

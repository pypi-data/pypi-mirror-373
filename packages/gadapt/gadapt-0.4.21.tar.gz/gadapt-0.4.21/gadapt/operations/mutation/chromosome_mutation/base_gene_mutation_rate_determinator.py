from abc import ABC, abstractmethod


class BaseGeneMutationRateDeterminator(ABC):
    def __init__(self) -> None:
        """
        Provides a framework for determining the number of mutation genes in a chromosome.
        """
        super().__init__()
        self.max_number_of_mutation_genes: int = -1

    def get_number_of_mutation_genes(
        self, chromosome, max_number_of_mutation_genes: int
    ):
        if max_number_of_mutation_genes is None:
            raise Exception("max_number_of_mutation_genes must not be None")
        if not chromosome:
            raise Exception("chromosome must not be None")
        self.chromosome = chromosome
        self.max_number_of_mutation_genes = max_number_of_mutation_genes
        return self._get_number_of_mutation_genes()

    @abstractmethod
    def _get_number_of_mutation_genes(self) -> int:
        pass

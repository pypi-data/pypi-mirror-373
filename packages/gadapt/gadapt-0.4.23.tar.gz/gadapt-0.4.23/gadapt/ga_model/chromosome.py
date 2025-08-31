"""
Chromosome
"""

from typing import List

import gadapt.adapters.string_operation.ga_strings as ga_strings
import gadapt.ga_model.definitions as definitions
from gadapt.ga_model.gene import Gene
from gadapt.ga_model.allele import Allele
from gadapt.ga_model.ranking_model import RankingModel


class Chromosome(RankingModel):
    def __init__(
        self,
        population_generation: int,
    ):
        """
        Chromosome class.
        Chromosome is a part of the Population. Chromosome consists of Gene's alleles'.
        Args:
            population_generation: population generation
        """
        super().__init__()
        self._parent_diversity_coefficient = float("NaN")
        self._cost_value = definitions.FLOAT_NAN
        self._is_immigrant = False
        self._population_generation = population_generation
        self._chromosome_id = None
        self._mutated_variables_id_list: List[int] = []
        self._first_mutant_generation = 0
        self._first_immigrant_generation = 0
        self._last_mutant_generation = 0
        self._last_immigrant_generation = 0
        self._chromosome_string = None
        self._mother_id = -1
        self._father_id = -1
        self._is_mutated = False
        self._is_immigrant = False
        self._genes: List[Allele] = []

    def __str__(self) -> str:
        return self._get_chromosome_string()

    def __getitem__(self, index) -> Allele:
        return self._genes[index]

    def __next__(self):
        return next(self._genes)

    def __len__(self):
        return len(self._genes)

    def __iter__(self):
        return ChromosomeIterator(self)

    def _get_sorted(self, key: None = None, reverse: bool = False):
        return sorted(self._genes, key=key, reverse=reverse)

    def append(self, g: Allele):
        """
        Appends a new gene value into the chromosome
        """
        self._genes.append(g)

    def clear(self):
        """
        Clears all genes from the chromosome
        """
        self._genes.clear()

    def _to_string(self):
        """
        Converts the chromosome to the string
        """
        return ga_strings.chromosome_to_string(self)

    def set_chromosome_string_none(self):
        """
        Sets the chromosome string to None
        """
        self._chromosome_string = None

    def _get_chromosome_string(self):
        if self._chromosome_string is None:
            self._chromosome_string = self._to_string()
        return self._chromosome_string

    @property
    def number_of_mutation_genes(self):
        """
        The number of mutated genes in the chromosome.
        """
        return self._number_of_mutation_genes

    @number_of_mutation_genes.setter
    def number_of_mutation_genes(self, value):
        self._number_of_mutation_genes = value

    @property
    def chromosome_id(self):
        """
        Id of the chromosme
        """
        return self._chromosome_id

    @chromosome_id.setter
    def chromosome_id(self, value):
        self._chromosome_id = value

    @property
    def cost_value(self):
        """
        Calculated cost value  of the chromosome
        """
        return self._cost_value

    @cost_value.setter
    def cost_value(self, value):
        self._cost_value = value

    @property
    def is_mutated(self) -> bool:
        """
        Indicates if the chromosome is mutated
        """
        return self._is_mutated

    @is_mutated.setter
    def is_mutated(self, value: bool):
        self._is_mutated = value

    @property
    def is_immigrant(self) -> bool:
        """
        Indicates if the chromosome is immigrant
        """
        return self._is_immigrant

    @is_immigrant.setter
    def is_immigrant(self, value: bool):
        self._is_immigrant = value

    @property
    def mother_id(self) -> int:
        """
        ID of mother chromosome
        """
        return self._mother_id

    @mother_id.setter
    def mother_id(self, value: int):
        self._mother_id = value

    @property
    def father_id(self) -> int:
        """
        ID of father chromosome
        """
        return self._father_id

    @father_id.setter
    def father_id(self, value: int):
        self._father_id = value

    def add_gene(self, gen_var: Gene, gen_var_value: float = definitions.FLOAT_NAN):
        """
        Adds a gene value to the chromosome
        """
        g = Allele(gen_var, gen_var_value)
        self.append(g)

    @property
    def parent_diversity_coefficient(self) -> float:
        """
        Diversity of parents
        """
        return self._parent_diversity_coefficient

    @parent_diversity_coefficient.setter
    def parent_diversity_coefficient(self, value: float):
        self._parent_diversity_coefficient = value

    @property
    def population_generation(self) -> int:
        """
        Population generation in which the chromosome appeared
        """
        return self._population_generation

    @population_generation.setter
    def population_generation(self, value: int):
        self._population_generation = value

    @property
    def chromosome_generation(self) -> int:
        """
        Generation of chromosome. It differs from the Population generation.
        It determines how many generations were needed for this chromosome to arise.
        """
        return self._chromosome_generation

    @chromosome_generation.setter
    def chromosome_generation(self, value: int):
        self._chromosome_generation = value

    @property
    def first_mutant_generation(self) -> int:
        """
        Indicates how many generations passed after a first mutation
        """
        return self._first_mutant_generation

    @first_mutant_generation.setter
    def first_mutant_generation(self, value: int):
        self._first_mutant_generation = value

    @property
    def last_mutant_generation(self) -> int:
        """
        Indicates how many generations passed after a last mutation
        """
        return self._last_mutant_generation

    @last_mutant_generation.setter
    def last_mutant_generation(self, value: int):
        self._last_mutant_generation = value

    @property
    def first_immigrant_generation(self) -> int:
        """
        Indicates how many generations passed after a first immigration
        """
        return self._first_immigrant_generation

    @first_immigrant_generation.setter
    def first_immigrant_generation(self, value: int):
        self._first_immigrant_generation = value

    @property
    def last_immigrant_generation(self) -> int:
        """
        Indicates how many generations passed after a last immigration
        """
        return self._last_immigrant_generation

    @last_immigrant_generation.setter
    def last_immigrant_generation(self, value: int):
        self._last_immigrant_generation = value

    @property
    def succ(self) -> bool:
        """
        Indicates if cost function execution succeded
        """
        return self._succ

    @succ.setter
    def succ(self, value: bool):
        self._succ = value

    @property
    def mutated_variables_id_list(self) -> List[int]:
        """
        List of mutated variables
        """
        return self._mutated_variables_id_list


class ChromosomeIterator:
    def __init__(self, chromosome):
        self.chromosome = chromosome
        self.index = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.index < len(self.chromosome._genes):
            result = self.chromosome._genes[self.index]
            self.index += 1
            return result
        else:
            raise StopIteration

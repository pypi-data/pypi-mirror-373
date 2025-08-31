import random
from abc import ABC, abstractmethod
from typing import List, Tuple

from gadapt.ga_model.chromosome import Chromosome


class BaseParentSelector(ABC):
    """
    Base Parent Selector

    Selects individuals for mating from the population
    """

    def __init__(self):
        super().__init__()
        self.population = None

    def select_mates(self, population) -> List[Tuple[Chromosome, Chromosome]]:
        """
        Selects and returns individuals for the crossover from the population
        Args:
            population: the population for the mates selection
        """
        self.population = population
        return self._select_mates_from_population()

    def _select_mates_from_population(self) -> List[Tuple[Chromosome, Chromosome]]:
        working_chromosomes = self._select_potential_parents()
        num_of_crossover_parents = self.population.options.number_of_crossover_parents
        working_chromosomes_len = len(working_chromosomes)
        if num_of_crossover_parents > working_chromosomes_len:
            num_of_crossover_parents = working_chromosomes_len
        working_chromosomes = working_chromosomes[:num_of_crossover_parents]
        working_chromosomes_len = len(working_chromosomes)
        random_number_for_reserve = random.randint(0, working_chromosomes_len - 1)
        reserve_chromosome = working_chromosomes[random_number_for_reserve]
        list_of_mates: List[Tuple[Chromosome, Chromosome]] = []
        while len(working_chromosomes) > 0:
            c1 = working_chromosomes.pop(0)
            if len(working_chromosomes) > 0:
                c2 = working_chromosomes.pop(0)
            else:
                c2 = reserve_chromosome
            list_of_mates.append((c1, c2))
        return list_of_mates

    @abstractmethod
    def _select_potential_parents(self):
        pass

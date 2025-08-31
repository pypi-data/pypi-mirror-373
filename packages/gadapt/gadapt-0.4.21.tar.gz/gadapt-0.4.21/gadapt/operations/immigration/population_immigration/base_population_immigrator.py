from abc import ABC, abstractmethod
from typing import Optional

from gadapt.ga_model.population import Population
from gadapt.ga_model.chromosome import Chromosome
from gadapt.operations.immigration.chromosome_immigration.base_chromosome_immigrator import (
    BaseChromosomeImmigrator,
)


class BasePopulationImmigrator(ABC):
    """
    Base class for population immigration
    """

    def __init__(self, chromosome_immigrator: BaseChromosomeImmigrator):
        self.population: Optional[Population] = None
        self._chromosome_immigrator = chromosome_immigrator

    def immigrate(self, population):
        """
        Immigrates chromosomes into the population
        Args:
            population: Population to immigrate new chromosomes
        """
        self.population = population
        self._immigrate_population()

    @abstractmethod
    def _immigrate_population(self):
        pass

    def _immigrate_chromosome(self, c: Chromosome):
        self._chromosome_immigrator.immigrate(c)

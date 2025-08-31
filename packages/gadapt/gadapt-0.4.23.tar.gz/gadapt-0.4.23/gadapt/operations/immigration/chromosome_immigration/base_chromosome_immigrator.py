from abc import ABC, abstractmethod


class BaseChromosomeImmigrator(ABC):
    """
    Base class for chromosome immigration
    """

    def __init__(self):
        super().__init__()
        self.chromosome = None

    def immigrate(self, c):
        """
        Makes one chromosome immigrant
        Args:
            c: chromosome to become the immigrant
        """
        self.chromosome = c
        self._immigrate_chromosome()
        self._chromosome_immigrated()

    @abstractmethod
    def _immigrate_chromosome(self):
        pass

    def _chromosome_immigrated(self):
        self.chromosome.is_immigrant = True
        if self.chromosome.first_immigrant_generation == 0:
            self.chromosome.first_immigrant_generation += 1
        self.chromosome.last_immigrant_generation = 1
        self.chromosome.first_mutant_generation = 0
        self.chromosome.last_mutant_generation = 0
        self.chromosome.set_chromosome_string_none()

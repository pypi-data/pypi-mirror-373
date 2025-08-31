import random
from typing import Tuple

from gadapt.operations.crossover.base_crossover import BaseCrossover
from gadapt.operations.chromosome_update.base_chromosome_updater import (
    BaseChromosomeUpdater,
)


class UniformCrossover(BaseCrossover):
    """
    Uniform Crossover. Genes from parents' chromosomes are combined in a uniform way.
    """

    def __init__(self, chromosome_updater: BaseChromosomeUpdater):
        super(UniformCrossover, self).__init__(chromosome_updater)

    def _combine(self) -> Tuple[float, float]:
        rnd = random.randint(0, 2)
        if rnd == 0:
            return self._father_allele.variable_value, self._mother_allele.variable_value
        elif rnd == 1:
            return self._father_allele.variable_value, self._father_allele.variable_value
        else:
            return self._mother_allele.variable_value, self._mother_allele.variable_value

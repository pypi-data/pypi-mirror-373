import random

from gadapt.operations.crossover.base_crossover import BaseCrossover
from gadapt.operations.chromosome_update.base_chromosome_updater import (
    BaseChromosomeUpdater,
)


class BlendingCrossover(BaseCrossover):
    """
    Blending Crossover combines
    gene values from the two parents into new variable values in offsprings.
    One value of the offspring variable comes from a combination of the two
    corresponding values of the parental genes
    """

    def __init__(self, chromosome_updater: BaseChromosomeUpdater):
        super(BlendingCrossover, self).__init__(chromosome_updater)
        self._current_gene_number = -1

    def _combine(self):
        gene = self._father_allele.gene
        val_father = self._father_allele.variable_value
        val_mother = self._mother_allele.variable_value
        x = 1
        if val_mother > val_father:
            x = -1
        beta_steps = random.randint(
            0, round(abs((val_father - val_mother) / gene.step))
        )
        val1 = round(
            val_father - (beta_steps * x) * gene.step,
            gene.decimal_places,
        )
        val2 = round(
            val_mother + (beta_steps * x) * gene.step,
            gene.decimal_places,
        )
        return val1, val2

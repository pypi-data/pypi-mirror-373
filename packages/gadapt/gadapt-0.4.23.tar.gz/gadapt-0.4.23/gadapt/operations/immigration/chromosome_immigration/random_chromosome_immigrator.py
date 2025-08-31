from gadapt.operations.immigration.chromosome_immigration.base_chromosome_immigrator import (
    BaseChromosomeImmigrator,
)


class RandomChromosomeImmigrator(BaseChromosomeImmigrator):
    """
    New immigrated chromosome with random genes
    """

    def _immigrate_chromosome(self):
        for g in self.chromosome:
            g.set_random_value()

from gadapt.ga_model.chromosome import Chromosome
from gadapt.ga_model.allele import Allele


class BaseChromosomeUpdater:
    """
    Updates chromosome
    """

    def chromosome_prepare_update(self, mother_gene: Allele, father_gene: Allele):
        pass

    def chromosome_update(self, offspring1: Chromosome, offspring2: Chromosome):
        pass

    def chromosome_start_update(self, *args, **kwargs):
        pass

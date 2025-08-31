from gadapt.ga_model.chromosome import Chromosome
from gadapt.ga_model.allele import Allele
from gadapt.utils import ga_utils
from gadapt.operations.chromosome_update.base_chromosome_updater import (
    BaseChromosomeUpdater,
)


class ParentDiversityChromosomeUpdater(BaseChromosomeUpdater):
    """
    Updates chromosome for the parent diversity purpose.
    """

    def __init__(self):
        self._genetic_diversity = None

    def _get_genetic_diversity(self, mother_gene, father_gene) -> float:
        return abs(mother_gene.variable_value - father_gene.variable_value) / (
            father_gene.gene.max_value - father_gene.gene.min_value
        )

    def _get_parent_diversity(self):
        return round(ga_utils.average(self._genetic_diversity), 2)

    def chromosome_prepare_update(self, mother_gene: Allele, father_gene: Allele):
        if mother_gene is None or father_gene is None:
            return
        self._genetic_diversity.append(
            self._get_genetic_diversity(mother_gene, father_gene)
        )

    def chromosome_update(self, offspring1: Chromosome, offspring2: Chromosome):
        parent_diversity = self._get_parent_diversity()
        offspring1.parent_diversity_coefficient = parent_diversity
        offspring2.parent_diversity_coefficient = parent_diversity

    def chromosome_start_update(self, *args, **kwargs):
        self._genetic_diversity = []

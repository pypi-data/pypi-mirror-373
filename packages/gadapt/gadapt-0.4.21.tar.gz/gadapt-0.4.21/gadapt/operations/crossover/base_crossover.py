import math
from abc import ABC, abstractmethod
from typing import Tuple, List

from gadapt.ga_model.allele import Allele
from gadapt.ga_model.chromosome import Chromosome
from gadapt.operations.chromosome_update.base_chromosome_updater import (
    BaseChromosomeUpdater,
)


class BaseCrossover(ABC):
    """Base Crossover Class"""

    def __init__(self, chromosome_updater: BaseChromosomeUpdater):
        self._current_gene_number = -1
        self._chromosome_updater = chromosome_updater

    def mate(self, chromosome_pairs: List[Tuple[Chromosome, Chromosome]], population):
        """
        Returns list of chromosome pairs using parents' genetic material

        Args:
            chromosome_pairs (List[Tuple[Chromosome, Chromosome]]) : List of chromosome pairs for mating
            population: Population
        """
        for chromosome1, chromosome2 in chromosome_pairs:
            offspring1, offspring2 = self._mate_pair(
                chromosome1, chromosome2, population.population_generation
            )
            population.add_chromosomes((offspring1, offspring2))
        current_len = len(population)
        chromosome_surplus = current_len - population.options.population_size
        if chromosome_surplus > 0:
            sorted_by_cost_value = sorted(
                population, key=lambda chrom: chrom.cost_value, reverse=True
            )
            i = 0
            for c in sorted_by_cost_value:
                if i >= chromosome_surplus:
                    break
                if not math.isnan(c.cost_value):
                    population.chromosomes.remove(c)

    def _mate_pair(
        self, mother: Chromosome, father: Chromosome, population_generation: int
    ):
        """Returns two offspring chromosomes using parents' genetic material

        Args:
            mother (Chromosome): The first chromosome for mating
            father (Chromosome): The second chromosome for mating
            population_generation (int): Current generation in the population

        Returns:
            Chromosome: the first offspring chromosome
            Chromosome: the second offspring chromosome
        """
        if len(mother) != len(father):
            raise Exception("Mother and father must have the same number of genes!")
        self._mother = mother
        self._father = father
        self._offspring1 = Chromosome(population_generation)
        self._offspring2 = Chromosome(population_generation)
        self._cross_genetic_material()
        self._increase_generation()
        return self._offspring1, self._offspring2

    def _cross_genetic_material(self):
        self._chromosome_updater.chromosome_start_update()
        number_of_genes = len(self._father)
        for self._current_gene_number in range(number_of_genes):
            self._mother_allele, self._father_allele = self._get_mother_father_allele()
            gene_father = self._mother_allele.gene
            gene_mother = self._father_allele.gene
            if gene_father != gene_mother:
                gene_mother = next(
                    (item.gene for item in self._mother if item.gene == gene_father),
                    None,
                )
            if gene_mother is None:
                raise Exception(
                    "chromosomes in crossover do not have the same structure!"
                )
            self._gene_crossed()
            var1, var2 = self._combine()
            self._offspring1.add_gene(gene_father, var1)
            self._offspring2.add_gene(gene_father, var2)
        self._all_genes_crossed()
        self._offspring1.mother_id = self._mother.chromosome_id
        self._offspring2.mother_id = self._mother.chromosome_id
        self._offspring1.father_id = self._father.chromosome_id
        self._offspring2.father_id = self._father.chromosome_id

    def _get_mother_father_allele(self) -> Tuple[Allele, Allele]:
        if self._current_gene_number == -1:
            raise Exception("_current_gene_number not set")
        father_allele = self._father[self._current_gene_number]
        mother_allele = self._mother[self._current_gene_number]
        return mother_allele, father_allele

    @abstractmethod
    def _combine(self):
        pass

    def _increase_generation(self):
        current_generation = self._mother.chromosome_generation
        if (
            current_generation == 0
            or current_generation < self._father.chromosome_generation
        ):
            current_generation = self._father.chromosome_generation
        current_generation += 1
        self._offspring1.chromosome_generation = current_generation
        self._offspring2.chromosome_generation = current_generation

        current_generation = 0
        if (
            self._mother.first_mutant_generation > 0
            or self._father.first_mutant_generation > 0
        ):
            current_generation = self._mother.first_mutant_generation
            if (
                current_generation == 0
                or self._father.first_mutant_generation > current_generation
            ):
                current_generation = self._father.first_mutant_generation
            current_generation += 1
        self._offspring1.first_mutant_generation = current_generation
        self._offspring2.first_mutant_generation = current_generation

        current_generation = 0
        if (
            self._mother.last_mutant_generation > 0
            or self._father.last_mutant_generation > 0
        ):
            current_generation = self._mother.last_mutant_generation
            if current_generation == 0 or (
                0 < self._father.last_mutant_generation < current_generation
            ):
                current_generation = self._father.last_mutant_generation
            current_generation += 1
        self._offspring1.last_mutant_generation = current_generation
        self._offspring2.last_mutant_generation = current_generation

        current_generation = 0
        if (
            self._mother.first_immigrant_generation > 0
            or self._father.first_immigrant_generation > 0
        ):
            current_generation = self._mother.first_immigrant_generation
            if (
                current_generation == 0
                or self._father.first_immigrant_generation > current_generation
            ):
                current_generation = self._father.first_immigrant_generation
            current_generation += 1
        self._offspring1.first_immigrant_generation = current_generation
        self._offspring2.first_immigrant_generation = current_generation

        current_generation = 0
        if (
            self._mother.last_immigrant_generation > 0
            or self._father.last_immigrant_generation > 0
        ):
            current_generation = self._mother.last_immigrant_generation
            if current_generation == 0 or (
                0 < self._father.last_immigrant_generation < current_generation
            ):
                current_generation = self._father.last_immigrant_generation
            current_generation += 1
        self._offspring1.last_immigrant_generation = current_generation
        self._offspring2.last_immigrant_generation = current_generation

    def _gene_crossed(self):
        self._chromosome_updater.chromosome_prepare_update(
            mother_gene=self._mother_allele, father_gene=self._father_allele
        )

    def _all_genes_crossed(self):
        self._chromosome_updater.chromosome_update(
            offspring1=self._offspring1, offspring2=self._offspring2
        )

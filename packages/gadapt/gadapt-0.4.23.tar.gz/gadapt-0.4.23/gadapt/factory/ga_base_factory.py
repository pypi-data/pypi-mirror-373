from abc import ABC, abstractmethod
from typing import Optional

from gadapt.ga_model.ga_options import GAOptions
from gadapt.operations.cost_finding.base_cost_finder import BaseCostFinder
from gadapt.operations.crossover.base_crossover import BaseCrossover
from gadapt.operations.exit_check.base_exit_checker import BaseExitChecker
from gadapt.operations.immigration.chromosome_immigration.base_chromosome_immigrator import (
    BaseChromosomeImmigrator,
)
from gadapt.operations.immigration.population_immigration.base_population_immigrator import (
    BasePopulationImmigrator,
)
from gadapt.operations.mutation.chromosome_mutation.base_gene_mutation_selector import (
    BaseGeneMutationSelector,
)
from gadapt.operations.mutation.gene_mutation.base_gene_mutator import BaseGeneMutator
from gadapt.operations.parent_selection.base_parent_selector import BaseParentSelector
from gadapt.operations.mutation.population_mutation.base_chromosome_mutation_selector import (
    BaseChromosomeMutationSelector,
)

"""
    Factory definition for creating  class instances based on GA options
"""


class BaseGAFactory(ABC):
    def __init__(self) -> None:
        super().__init__()
        self.population_updater = None
        self._ga = None
        self._options = None
        self.gene_updater = None
        self.cost_finder: Optional[BaseCostFinder] = None
        self.population_immigrator: Optional[BasePopulationImmigrator] = None
        self.chromosome_immigrator: Optional[BaseChromosomeImmigrator] = None
        self.gene_mutator: Optional[BaseGeneMutator] = None
        self.gene_mutation_selector: Optional[BaseGeneMutationSelector] = None
        self.chromosome_mutation_selector: Optional[BaseChromosomeMutationSelector] = (
            None
        )
        self.parent_selector: Optional[BaseParentSelector] = None
        self.exit_checker: Optional[BaseExitChecker] = None
        self.crossover: Optional[BaseCrossover] = None

    def initialize_factory(self, ga):
        self._ga = ga
        self._options = GAOptions(ga)

    def get_cost_finder(self) -> BaseCostFinder:
        """
        Cost Finder instance
        """
        if self.cost_finder is None:
            self.cost_finder = self._get_cost_finder()
        return self.cost_finder

    def get_population_immigrator(self) -> BasePopulationImmigrator:
        """
        Population Immigrator Instance
        """
        if self.population_immigrator is None:
            self.population_immigrator = self._get_population_immigrator()
        return self.population_immigrator

    def get_chromosome_immigrator(self) -> BaseChromosomeImmigrator:
        """
        Chromosome Immigrator Instance
        """
        if self.chromosome_immigrator is None:
            self.chromosome_immigrator = self._get_chromosome_immigrator()
        return self.chromosome_immigrator

    def get_gene_mutation_selector(self) -> BaseGeneMutationSelector:
        """
        Gene Mutation Selector Instance
        """
        if self.gene_mutation_selector is None:
            self.gene_mutation_selector = self._get_gene_mutation_selector()
        return self.gene_mutation_selector

    def get_gene_mutator(self) -> BaseGeneMutator:
        """
        Allele Mutator Instance
        """
        if self.gene_mutator is None:
            self.gene_mutator = self._get_gene_mutator()
        return self.gene_mutator

    def get_chromosome_mutation_selector(self) -> BaseChromosomeMutationSelector:
        """
        Chromosome Mutation Selector Instance
        """
        if self.chromosome_mutation_selector is None:
            self.chromosome_mutation_selector = self._get_chromosome_mutation_selector()
        return self.chromosome_mutation_selector

    def get_parent_selector(self) -> BaseParentSelector:
        """
        Parent Selector Instance
        """
        if self.parent_selector is None:
            self.parent_selector = self._get_parent_selector()
        return self.parent_selector

    def get_exit_checker(self) -> BaseExitChecker:
        """
        Exit Checker Instance
        """
        if self.exit_checker is None:
            self.exit_checker = self._get_exit_checker()
        return self.exit_checker

    def get_gene_updater(self):
        """
        Gene Updater Instance
        """
        if self.gene_updater is None:
            self.gene_updater = self._get_gene_updater()
        return self.gene_updater

    def get_population_updater(self):
        """
        Population Updater Instance
        """
        if self.population_updater is None:
            self.population_updater = self._get_population_updater()
        return self.population_updater

    def get_crossover(self) -> BaseCrossover:
        """
        Crossover Instance
        """
        if self.crossover is None:
            self.crossover = self._get_crossover()
        return self.crossover

    @abstractmethod
    def _get_cost_finder(self) -> BaseCostFinder:
        """
        Cost Finder instance
        """
        pass

    @abstractmethod
    def _get_population_immigrator(self) -> BasePopulationImmigrator:
        """
        Population Immigrator Instance
        """
        pass

    @abstractmethod
    def _get_chromosome_immigrator(self) -> BaseChromosomeImmigrator:
        """
        Chromosome Immigrator Instance
        """
        pass

    @abstractmethod
    def _get_gene_mutation_selector(self) -> BaseGeneMutationSelector:
        """
        Chromosome Mutator Instance
        """
        pass

    @abstractmethod
    def _get_gene_mutator(self) -> BaseGeneMutator:
        """
        Allele Mutator Instance
        """
        pass

    @abstractmethod
    def _get_chromosome_mutation_selector(self) -> BaseChromosomeMutationSelector:
        """
        Population Mutator Instance
        """
        pass

    @abstractmethod
    def _get_parent_selector(self) -> BaseParentSelector:
        """
        Parent Selector Instance
        """
        pass

    @abstractmethod
    def _get_exit_checker(self) -> BaseExitChecker:
        """
        Exit Checker Instance
        """
        pass

    @abstractmethod
    def _get_gene_updater(self):
        """
        Gene Updater Instance
        """
        pass

    @abstractmethod
    def _get_population_updater(self):
        """
        Population Updater Instance
        """
        pass

    @abstractmethod
    def _get_crossover(self) -> BaseCrossover:
        """
        Crossover Instance
        """
        pass

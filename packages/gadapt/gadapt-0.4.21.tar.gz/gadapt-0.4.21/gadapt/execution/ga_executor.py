from typing import List, Tuple, Optional

import gadapt.ga_model.message_levels as message_levels
from gadapt.ga_model.chromosome import Chromosome
from gadapt.adapters.ga_logging.logging_settings import init_logging
from gadapt.factory.ga_factory import BaseGAFactory
from gadapt.ga_model.ga_options import GAOptions
from gadapt.ga_model.ga_results import GAResults
from gadapt.ga_model.population import Population


class GAExecutor:
    """
    Executor for the genetic algorithm

    Args:
        ga_options (GAOptions): Options for GA execution
        factory (GAFactory): Factory for objects creation
    """

    def __init__(self, ga_options: GAOptions, factory: BaseGAFactory) -> None:
        self.population: Optional[Population] = None
        if ga_options is not None:
            self.ga_options = ga_options
        self.factory = factory
        self.chromosome_mutator = self.factory.get_gene_mutation_selector()
        self.population_mutator = self.factory.get_chromosome_mutation_selector()
        self.exit_checker = self.factory.get_exit_checker()
        self.cost_finder = self.factory.get_cost_finder()
        self.population_immigrator = self.factory.get_population_immigrator()
        self.chromosome_immigrator = self.factory.get_chromosome_immigrator()
        self.selector = self.factory.get_parent_selector()
        self.crossover = self.factory.get_crossover()
        self.gene_updater = self.factory.get_gene_updater()
        self.population_updater = self.factory.get_population_updater()
        self.gene_mutator = self.factory.get_gene_mutator()

    def execute(self) -> GAResults:
        """
        Executes the genetic algorithm
        """
        self.population = Population(self.ga_options)
        if self.population is None:
            raise Exception("population object is None!")
        results = GAResults()
        try:
            init_logging(self.ga_options.logging)
        except Exception as ex:
            results.messages.append(
                (
                    message_levels.WARNING,
                    "Logging failed. Error message: {exc}".format(exc=str(ex)),
                )
            )
            self.ga_options.logging = False
        try:
            self.find_costs()
            while not self.exit():
                self.immigrate()
                self.mate()
                self.mutate()
                self.find_costs()
            if self.population.timeout_expired:
                results.messages.append((message_levels.WARNING, "Timeout expired!"))
            best_individual = self.population.best_individual
            results.min_cost = self.population.min_cost
            results.number_of_iterations = self.population.population_generation
            results.min_cost_per_generation = self.population.min_cost_per_generation
            for g in best_individual:
                results.result_values[g.gene.variable_id] = g.variable_value
        except Exception as ex:
            results.success = False
            results.messages.append((message_levels.ERROR, str(ex)))
        return results

    def exit(self) -> bool:
        """
        Check exit from the GA
        """
        if self.population is None:
            raise Exception("population object must not be None!")
        self.population.population_generation += 1
        return self.exit_checker.check(self.population)

    def find_costs(self):
        """
        Finds costs for chromosomes
        """
        self.population.previous_avg_cost = self.population.avg_cost
        self.population.previous_min_cost = self.population.min_cost
        self.cost_finder.find_costs(self.population)
        self.gene_updater.update_genes(self.population)
        self.population_updater.update_population(self.population)

    def immigrate(self):
        """
        Immigrates new chromosomes
        """
        self.population_immigrator.immigrate(self.population)

    def mate(self):
        """
        Mates chromosomes
        """
        chromosome_pairs = self.select_mates()
        self.crossover.mate(chromosome_pairs, self.population)

    def mutate(self):
        """
        Mutates chromosomes in the population
        """
        self.population_mutator.mutate(self.population)

    def select_mates(self) -> List[Tuple[Chromosome, Chromosome]]:
        """
        Selects mates for pairing
        """
        return self.selector.select_mates(self.population)

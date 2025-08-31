import sys
import traceback
from abc import ABC, abstractmethod
from typing import Optional

from gadapt.ga_model.population import Population
from gadapt.ga_model.chromosome import Chromosome


class BaseCostFinder(ABC):
    """
    Base class for cost finding
    """

    def __init__(self):
        super().__init__()
        self.population: Optional[Population] = None

    def _execute_function(self, cost_function, c: Chromosome):
        """
        Executes the cost function

        Args:
            cost_function: Function to execute
            c (Chromosome): The chromosome with
            genes containing values for the function execution.
        """
        var_dict = {}
        for g in c:
            var_dict[g.gene.variable_id] = g.variable_value
        try:
            sorted_var_dict = dict(sorted(var_dict.items()))
            cost_value = cost_function(list(sorted_var_dict.values()))
            c.cost_value = cost_value
        except Exception as ex:
            print(ex)
            traceback.print_exc()
            c.succ = False
            c.cost_value = sys.float_info.max

    @abstractmethod
    def _find_costs_for_population(self):
        pass

    def find_costs(self, population):
        """
        Finds costs for the population

        Args:
            population (Population): The population to find costs for each chromosome
        """
        self.population = population
        self._find_costs_for_population()
        self.population.min_cost_per_generation.append(self.population.min_cost)

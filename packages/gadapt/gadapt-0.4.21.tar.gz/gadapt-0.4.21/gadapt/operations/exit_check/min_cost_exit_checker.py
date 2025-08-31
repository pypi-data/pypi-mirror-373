from gadapt.operations.exit_check.base_exit_checker import BaseExitChecker


class MinCostExitChecker(BaseExitChecker):
    """
    Exit check based on minimal cost.
    The GA exits when there is no improvement in the minimal cost in a
    defined number of iterations.
    """

    def _is_exit(self):
        if self.population is None:
            raise Exception("population must not be null")
        return self.population.min_cost >= self.population.previous_min_cost

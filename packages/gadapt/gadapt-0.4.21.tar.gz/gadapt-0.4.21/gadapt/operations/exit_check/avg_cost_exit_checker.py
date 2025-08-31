from gadapt.operations.exit_check.base_exit_checker import BaseExitChecker


class AvgCostExitChecker(BaseExitChecker):
    """
    Exit check based on average cost.
    The GA exits when there is no improvement in
    the average cost of the kept population in a defined number of iterations.
    """

    def _is_exit(self):
        if self.population is None:
            raise Exception("population must not be null")
        return self.population.avg_cost >= self.population.previous_avg_cost

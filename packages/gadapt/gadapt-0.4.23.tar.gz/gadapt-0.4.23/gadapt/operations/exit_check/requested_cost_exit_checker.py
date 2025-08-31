from gadapt.operations.exit_check.base_exit_checker import BaseExitChecker


class RequestedCostExitChecker(BaseExitChecker):
    """
    Exit check based on requested cost.
    The GA exits when the minimum cost reaches a defined value.
    """

    def __init__(self, requested_cost: float) -> None:
        super().__init__(1)
        self.requested_cost = requested_cost

    def _is_exit(self):
        if self.population.min_cost <= self.requested_cost:
            return True
        return False

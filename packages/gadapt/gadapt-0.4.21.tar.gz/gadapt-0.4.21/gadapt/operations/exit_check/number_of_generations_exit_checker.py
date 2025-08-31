from gadapt.operations.exit_check.base_exit_checker import BaseExitChecker


class NumberOfGenerationsExitChecker(BaseExitChecker):
    """
    Exit check based on the number of generations.
    The GA exits when the defined number of generations is reached.
    """

    def __init__(self, number_of_generations: float) -> None:
        super().__init__(1)
        self.number_of_generations = number_of_generations

    def _is_exit(self):
        if self.population.population_generation >= self.number_of_generations:
            return True
        return False

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional

from gadapt.adapters.ga_logging.logging_settings import gadapt_log_info
from gadapt.ga_model.population import Population


class BaseExitChecker(ABC):
    """
    Base class for exit check
    Args:
        max_attempt_no (int): Maximal number of attempts with no improvement,
        for the given criteria.

            After this number of attempts with no improvements, the GA exits
    """

    def __init__(self, max_attempt_no: int) -> None:
        self.max_attempt_no = max_attempt_no
        self.attempt_no = 0
        self.population: Optional[Population] = None

    @property
    def attempt_no(self) -> int:
        return self._attempt_no

    @attempt_no.setter
    def attempt_no(self, value: int):
        self._attempt_no = value

    def check(self, population: Population):
        self.population = population
        if self.population is None:
            raise Exception("Population is None!")
        if self.population is None:
            raise Exception("Population is None!")
        time_diff = (datetime.now() - self.population.start_time).total_seconds()
        if time_diff >= self.population.options.timeout:
            self.population.timeout_expired = True
            return True
        if self._is_exit():
            self.attempt_no += 1
        else:
            self.attempt_no = 0
        if self.attempt_no >= self.max_attempt_no:
            gadapt_log_info("function exit.")
            return True
        return False

    @abstractmethod
    def _is_exit(self) -> bool:
        pass

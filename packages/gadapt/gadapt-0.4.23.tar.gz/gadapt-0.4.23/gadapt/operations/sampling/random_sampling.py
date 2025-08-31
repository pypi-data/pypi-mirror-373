import random
from typing import List

from gadapt.operations.sampling.base_sampling import T, BaseSampling


class RandomSampling(BaseSampling):
    """
    "Random" algorithm for extracting a sample from the population.
    """

    def _prepare_sample(self, lst: List[T]) -> List[T]:
        members_for_action = random.sample(lst, len(lst))
        return [
            m.set_rank_and_return(rank)
            for rank, m in enumerate(members_for_action[: self.max_num])
        ]

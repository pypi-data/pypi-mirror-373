from typing import List

from gadapt.operations.sampling.base_sampling import T, BaseSampling


class FromTopToBottomSampling(BaseSampling):
    """
    "From Top To Bottom" algorithm for extracting a sample from the population.
    """

    def _prepare_sample(self, lst: List[T]) -> List[T]:
        members_for_action = sorted(lst, key=self._sort_key)
        return [
            m.set_rank_and_return(rank)
            for rank, m in enumerate(members_for_action[: self.max_num])
        ]

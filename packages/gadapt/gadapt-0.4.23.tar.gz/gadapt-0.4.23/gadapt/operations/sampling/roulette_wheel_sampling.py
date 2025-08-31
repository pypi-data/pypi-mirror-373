import random
from typing import List

from gadapt.operations.sampling.base_sampling import T, BaseSampling


class RouletteWheelSampling(BaseSampling):
    """
    "RouletteWheel" (also known as "Weighted Random Pairing") algorithm for\
        extracting a sample from the population.
    """

    def _prepare_sample(self, lst: List[T]) -> List[T]:
        """
        Prepares a sample from a list of objects.
        It calculates the cumulative probabilities for each object based on their rank
        and uses these probabilities to select objects for the sample.
        """
        rank_sum = sum(range(1, len(lst) + 1))
        cumulative_probability_list: List[float] = []
        action_probability = 0.0
        n_keep = len(lst)
        for j in range(len(lst)):
            n = n_keep - j
            probability_for_action = float(n_keep - n + 1) / float(rank_sum)
            action_probability += probability_for_action
            cumulative_probability_list.append(action_probability)
        rank = 0
        unallocated_members = [rm for rm in lst]
        unallocated_members.sort(key=self._sort_key, reverse=True)
        members_for_action = []
        for j in range(self.max_num):
            if len(unallocated_members) == 0:
                continue
            for i_c_p_l, m in enumerate(unallocated_members):
                m.action_probability = cumulative_probability_list[i_c_p_l]
            rnd_value = random.random()
            max_prob = (
                max(unallocated_members, key=lambda m: m.action_probability)
            ).action_probability
            rnd_value = rnd_value * max_prob
            mem = next(
                mb for mb in unallocated_members if mb.action_probability >= rnd_value
            )
            if mem is not None:
                rank += 1
                mem.rank = rank
                members_for_action.append(mem)
            unallocated_members = [um for um in unallocated_members if um.rank == -1]
        members_for_action.sort(key=lambda g: g.rank)
        return members_for_action

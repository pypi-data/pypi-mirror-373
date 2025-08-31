"""
Ranking model
"""

import gadapt.ga_model.definitions as definitions


class RankingModel:
    def __init__(self):
        """
        Base class for the object that can be ranked\
            (chromosomes and genes), for sampling purposes.
        """
        self._rank = -1
        self._cummulative_probability = definitions.FLOAT_NAN

    @property
    def rank(self):
        """
        Rank of the object
        """
        return self._rank

    @rank.setter
    def rank(self, value):
        self._rank = value

    @property
    def action_probability(self):
        """
        A probability for executing some action (e.allele. pairing or mutation)
        """
        return self._cummulative_probability

    @action_probability.setter
    def action_probability(self, value):
        self._cummulative_probability = value

    def set_rank_and_return(self, rank):
        """
        Sets rank for the object and returns the object
        """
        self.rank = rank
        return self

    def reset_for_sampling(self):
        """
        Resets object properties for the purpose of a new sampling
        """
        self._rank = -1
        self._cummulative_probability = definitions.FLOAT_NAN

import random

from gadapt.operations.mutation.gene_mutation.random_gene_mutator import (
    RandomGeneMutator,
)
from gadapt.utils.ga_utils import get_rand_bool, get_rand_bool_with_probability


# *** Obsolete ***
class ExtremePointedGeneMutator(RandomGeneMutator):
    def _make_mutated_value(self):
        return self._make_mutation()

    def _make_rounded_random_value_below_or_above(self):
        return round(
            self._make_random_value_below_or_above(),
            self.gene_value.gene.decimal_places,
        )

    def _make_random_value_below_or_above(self):
        if get_rand_bool():
            return self._make_random_value_above()
        return self._make_random_value_below()

    def _make_random_value_below(self):
        if self.gene_value.variable_value == self.gene_value.gene.min_value:
            return self.gene_value.gene.make_random_value()
        number_of_steps = random.randint(
            0,
            round(
                (self.gene_value.variable_value - self.gene_value.gene.min_value)
                / self.gene_value.gene.step
            ),
        )
        return (
            self.gene_value.gene.min_value + number_of_steps * self.gene_value.gene.step
        )

    def _make_random_value_above(self):
        if self.gene_value.variable_value == self.gene_value.gene.max_value:
            return self.gene_value.gene.make_random_value()
        number_of_steps = random.randint(
            0,
            round(
                (self.gene_value.gene.max_value - self.gene_value.variable_value)
                / self.gene_value.gene.step
            ),
        )
        return (
            self.gene_value.variable_value + number_of_steps * self.gene_value.gene.step
        )

    def _get_mutate_func(self):
        prob = self.gene_value.gene.cross_diversity_coefficient
        if prob > 1.0:
            prob = 1.0
        should_mutate_random = get_rand_bool_with_probability(prob)
        if should_mutate_random:
            return super()._make_mutated_value
        else:
            return self._make_rounded_random_value_below_or_above

    def _make_mutation(self):
        f = self._get_mutate_func()
        return f()

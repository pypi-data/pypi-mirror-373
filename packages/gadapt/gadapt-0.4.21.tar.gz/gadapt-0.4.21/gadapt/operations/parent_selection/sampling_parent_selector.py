from gadapt.operations.parent_selection.base_parent_selector import BaseParentSelector
from gadapt.operations.sampling.base_sampling import BaseSampling


class SamplingParentSelector(BaseParentSelector):
    """
    Parent Selector based on sampling.
    Sampling is the algorithm for extracting a sample from the population,
    based on specific value of the chromosme.
    In this case sampling depends on cost value.

    Selects mates for mating from the population
    """

    def __init__(self, sampling: BaseSampling) -> None:
        super().__init__()
        self._sampling = sampling

    def _select_potential_parents(self):
        return self._sampling.get_sample(
            self.population.chromosomes, len(self.population), lambda c: c.cost_value
        )

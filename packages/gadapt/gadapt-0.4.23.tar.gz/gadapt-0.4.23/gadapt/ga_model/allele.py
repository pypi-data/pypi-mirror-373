"""
Allele
"""

import math

import gadapt.adapters.string_operation.ga_strings as ga_strings
import gadapt.ga_model.definitions as definitions
from gadapt.ga_model.gene import Gene
from gadapt.ga_model.ranking_model import RankingModel


class Allele(RankingModel):
    def __init__(self, gen_variable, var_value=None):
        """
        Allele class. Allele is a part of chromosome.
        It contains concrete value of Gene.
        Args:
            gen_variable: Gene which defines the allele
            var_value: Variable value
        """
        super().__init__()
        self.gene = gen_variable
        self.variable_value = var_value
        self._rank = -1
        self._cummulative_probability = definitions.FLOAT_NAN
        if self.variable_value is None or math.isnan(self.variable_value):
            self.set_random_value()

    def __str__(self) -> str:
        return self._to_string()

    def _to_string(self):
        return ga_strings.gene_value_to_string(self)

    @property
    def gene(self) -> Gene:
        """
        Gene which defines the allele
        """
        return self._gene

    @gene.setter
    def gene(self, value: Gene):
        if not isinstance(value, Gene):
            raise
        self._gene = value

    @property
    def variable_value(self):
        """
        Variable value
        """
        return self._variable_value

    @variable_value.setter
    def variable_value(self, value):
        self._variable_value = value

    def set_random_value(self):
        """
        Sets a random value for the variable_value property
        """
        self.variable_value = self.gene.make_random_value()

import statistics as stat

from gadapt.ga_model.gene import Gene
from gadapt.operations.gene_update.base_gene_updater import BaseGeneUpdater


class CrossDiversityGeneUpdater(BaseGeneUpdater):
    """
    Common variable updater
    """

    def _update_genes(self):
        def scale_values(g: Gene, values):
            scaled_values = []
            if g.min_value == g.max_value:
                return [0.5] * len(
                    values
                )  # If min_val and max_val are the same, return a list of 0.5s

            for value in values:
                scaled_value = (value - g.min_value) / (g.max_value - g.min_value)
                scaled_values.append(scaled_value)
            return scaled_values

        unique_values_per_variables = {}
        values_per_variables = {}
        for c in self.population:
            if c.is_immigrant:
                continue
            for g in c:
                unique_var_values = unique_values_per_variables.get(g.gene, None)
                var_values = values_per_variables.get(g.gene, None)
                if unique_var_values is None:
                    unique_var_values = set()
                    unique_values_per_variables[g.gene] = unique_var_values
                if var_values is None:
                    var_values = []
                    values_per_variables[g.gene] = var_values
                unique_var_values.add(g.variable_value)
                var_values.append(g.variable_value)
        for key in unique_values_per_variables:
            if len(unique_values_per_variables[key]) == 1:
                key.stacked = True
            else:
                key.stacked = False
        for key in values_per_variables:
            if key.stacked:
                key.cross_diversity_coefficient = 0.0
                continue
            values_scaled = scale_values(key, values_per_variables[key])
            st_dev = stat.stdev(values_scaled)
            if key.initial_st_dev < 0:
                key.initial_st_dev = st_dev
            if max(values_scaled) - min(values_scaled) == 0:
                key.cross_diversity_coefficient = 0.0
            else:
                key.cross_diversity_coefficient = st_dev / key.initial_st_dev

import gadapt.ga_model.definitions as definitions
from gadapt.adapters.validation.base_options_validator import BaseOptionsValidator


class CommonOptionsValidator(BaseOptionsValidator):
    """
    Common class for options validation
    """

    def __init__(self, options) -> None:
        super().__init__(options)
        self._validation_messages = []

    def _validate_options(self):
        self.success &= self._check_nones_types_and_values()
        self.success &= self._check_genes()
        self.success &= self._check_cost_function()

    def _check_genes(self) -> bool:
        if self.options._genes is None:
            return False
        rslt = True
        for v in self.options._genes:
            if v.min_value is None or v.max_value is None or v.step is None:
                self._add_message(
                    "Min value, max value and step must not be\
                        None! (Variable {var_no})".format(
                        var_no=v.variable_id
                    )
                )
                rslt &= False
            elif (
                not (isinstance(v.min_value, float) or isinstance(v.min_value, int))
                or not (isinstance(v.max_value, float) or isinstance(v.max_value, int))
                or not (isinstance(v.step, float) or isinstance(v.step, int))
            ):
                self._add_message(
                    "Min value, max value and step must be float or int\
                        values! (Variable {var_no})".format(
                        var_no=v.variable_id
                    )
                )
                rslt &= False
            elif v.min_value > v.max_value:
                self._add_message(
                    "Min value must be less or equal than max value!\
                        (Variable {var_no})".format(
                        var_no=v.variable_id
                    )
                )
                rslt &= False
            elif v.step <= 0.0:
                self._add_message(
                    "Step must be positive float value! (Variable {var_no})".format(
                        var_no=v.variable_id
                    )
                )
                rslt &= False
            elif v.min_value + v.step > v.max_value:
                self._add_message(
                    "Invalid step value! (Variable {var_no})".format(
                        var_no=v.variable_id
                    )
                )
                rslt &= False
            if v.decimal_places < 0:
                self._add_message(
                    "Invalid number of decimal places! (Variable {var_no})".format(
                        var_no=v.variable_id
                    )
                )
                rslt &= False
        return rslt

    def _check_cost_function(self):
        if self.options.cost_function is None:
            self._add_message("Cost Function must not be None!")
            return False
        elif not callable(self.options.cost_function):
            self._add_message("Cost Function must be callable!")
            return False
        argsmin = []
        argsmax = []
        for v in self.options._genes:
            argsmin.append(v.min_value)
            argsmax.append(v.max_value)
        try:
            func_result_min = self.options.cost_function(argsmin)
            func_result_max = self.options.cost_function(argsmax)
            if not isinstance(func_result_min, float) or not isinstance(
                func_result_max, float
            ):
                self._add_message("The function must return float value!")
                return False
        except KeyError:
            self._add_message(
                "Inadequate number of parameters for the passed function!"
            )
            return False
        except Exception as ex:
            self._add_message(
                "An exception raised on the function call: {exc}".format(exc=str(ex))
            )
            return False
        return True

    def _check_nones_types_and_values(self) -> bool:
        rslt = True
        population_size = 0
        if self.options.population_size is None:
            self._add_message("Population size must not be None!")
            rslt &= False
        elif not isinstance(self.options.population_size, int):
            self._add_message("Population size type must be int!")
            rslt &= False
        elif self.options.population_size < 4 or self.options.population_size > 65536:
            self._add_message("Population size must be an int between 4 and 65536!")
            rslt &= False
        else:
            population_size = self.options.population_size
        keep_elitism_percentage = self.options.keep_elitism_percentage
        if not (0 <= self.options.keep_elitism_percentage <= 100):
            self._add_message("Elitism percentage value must be between 0 and 100!")
            rslt &= False
        immigration_number = 0
        if self.options.immigration_number is None:
            self._add_message("Immigration Number must not be None!")
            rslt &= False
        elif not isinstance(self.options.immigration_number, int):
            self._add_message("Immigration Number must be type int!")
            rslt &= False
        elif (
            population_size > 0
            and self.options.immigration_number > population_size - 1
        ):
            self._add_message(
                "Immigration Number must not be type same or greater\
                    than population size!"
            )
            rslt &= False
        elif self.options.immigration_number < 0:
            self._add_message("Immigration Number must ne eqals or greather than 0!")
            rslt &= False
        else:
            immigration_number = self.options.immigration_number
        if (
            self.options.number_of_mutation_chromosomes is None
            and self.options.percentage_of_mutation_chromosomes is None
        ):
            self._add_message(
                "Number of Mutation Chromosomes or Percentage of Mutation\
                    Chromosomes must not be None!"
            )
            rslt &= False
        elif not isinstance(
            self.options.number_of_mutation_chromosomes, int
        ) and not isinstance(self.options.percentage_of_mutation_chromosomes, float):
            self._add_message(
                "Number of Mutation Chromosomes must be type int or Percentage\
                    of Mutation Chromosomes must be float!"
            )
            rslt &= False
        else:
            if (
                (self.options.number_of_mutation_chromosomes is not None)
                and (isinstance(self.options.number_of_mutation_chromosomes, int))
                and (self.options.number_of_mutation_chromosomes > 0)
            ):
                if (
                    population_size > 0
                    and self.options.number_of_mutation_chromosomes
                    > round(population_size * (keep_elitism_percentage / 100))
                    - immigration_number
                ):
                    self._add_message(
                        "Invalid number of mutation chromosomes: {0}".format(
                            str(self.options.number_of_mutation_chromosomes)
                        )
                    )
                    rslt &= False
            elif (self.options.percentage_of_mutation_chromosomes is None) or (
                not isinstance(self.options.percentage_of_mutation_chromosomes, float)
            ):
                self._add_message(
                    "Number of Mutation Chromosomes must have int\
                        value >=0 or Percentage of\
                        Mutation Chromosomes must have float (0.0-100.0) value! "
                )
                rslt &= False
            elif (
                self.options.percentage_of_mutation_chromosomes < 0.0
                or self.options.percentage_of_mutation_chromosomes > 100.0
            ):
                self._add_message(
                    "Invalid percentage of mutation chromosomes: {0} and number\
                        of mutation chromosomes: {1}".format(
                        str(self.options.percentage_of_mutation_chromosomes),
                        str(self.options.number_of_mutation_chromosomes),
                    )
                )
                rslt &= False
        if self.options._genes is None:
            self._add_message("Genes must not be None!")
            rslt &= False
        num_of_genes = len(self.options._genes)  # type: ignore
        if num_of_genes < 1:
            self._add_message("At least one gene must be added!")
            rslt &= False
        if (
            self.options.number_of_mutation_genes is None
            and self.options.percentage_of_mutation_genes is None
        ):
            self._add_message(
                "Number Of Mutation Genes or Percentage Of\
                    Mutation Genes must not be None!"
            )
            rslt &= False
        elif not isinstance(
            self.options.number_of_mutation_genes, int
        ) and not isinstance(self.options.percentage_of_mutation_genes, float):
            self._add_message(
                "Number Of Mutation Genes must have int value >=0 or Percentage of\
                    Mutation Genes must have float (0.0-100.0) value!"
            )
            rslt &= False
        elif (
            (self.options.number_of_mutation_genes is not None)
            and isinstance(self.options.number_of_mutation_genes, int)
            and (self.options.number_of_mutation_genes > 0)
        ):
            if (
                num_of_genes > 0
                and self.options.number_of_mutation_genes > num_of_genes
            ):
                self._add_message(
                    "Invalid number of mutation genes: {0}".format(
                        str(self.options.number_of_mutation_genes)
                    )
                )
                rslt &= False
        elif (self.options.percentage_of_mutation_genes is None) or (
            not isinstance(self.options.percentage_of_mutation_genes, float)
        ):
            self._add_message(
                "Number of Mutation Genes must have int value or Percentage\
                    of Mutation Genes must have float value! "
            )
            rslt &= False
        elif (
            self.options.percentage_of_mutation_genes < 0.0
            or self.options.percentage_of_mutation_genes > 100.0
        ):
            self._add_message(
                "Invalid percentage of mutation genes: {} and number of\
                    mutation genes: {}".format(
                    str(self.options.percentage_of_mutation_genes),
                    str(self.options.number_of_mutation_genes),
                )
            )
            rslt &= False
        if self.options.max_attempt_no is None:
            self._add_message("Max Attempt No must not be None!")
            rslt &= False
        elif not isinstance(self.options.max_attempt_no, int):
            self._add_message("Max Attempt No must be type int!")
            rslt &= False
        elif self.options.max_attempt_no < 1 or self.options.max_attempt_no > 65536:
            self._add_message("Max Attempt No must be type an int between 1 and 65536!")
            rslt &= False
        if (
            self.options.chromosome_mutation == definitions.CROSS_DIVERSITY
            or definitions.CROSS_DIVERSITY in self.options.chromosome_mutation
        ):
            if self.options.cross_diversity_mutation_gene_sampling is None:
                self._add_message(
                    "Cross Diversity Mutation Gene Sampling must not be None!"
                )
                rslt &= False
            elif not isinstance(
                self.options.cross_diversity_mutation_gene_sampling, str
            ):
                self._add_message(
                    "Cross Diversity Mutation Gene Sampling must be type str!"
                )
                rslt &= False
        if self.options.chromosome_mutation is None:
            self._add_message("Chromosome Mutation must not be None!")
            rslt &= False
        elif not isinstance(self.options.chromosome_mutation, str):
            self._add_message("Chromosome Mutation must be type str!")
            rslt &= False
        elif definitions.PARAM_SEPARATOR in self.options.chromosome_mutation:
            mutator_strings = [
                ms.strip()
                for ms in self.options.chromosome_mutation.split(
                    definitions.PARAM_SEPARATOR
                )
            ]
            for mutator_string in mutator_strings:
                if mutator_string not in definitions.CHROMOSOME_MUTATION_STRINGS:
                    self._add_message(
                        "Invalid value of Chromosome Mutation:\
                            {0}. Allowed values: {1}".format(
                            mutator_string,
                            self._get_allowed_values(
                                definitions.CHROMOSOME_MUTATION_STRINGS
                            ),
                        )
                    )
                    rslt &= False
        elif (
            self.options.chromosome_mutation
            not in definitions.CHROMOSOME_MUTATION_STRINGS
        ):
            self._add_message(
                "Invalid value of Chromosome Mutation: {0}. Allowed values: {1}".format(
                    self.options.chromosome_mutation,
                    self._get_allowed_values(definitions.CHROMOSOME_MUTATION_STRINGS),
                )
            )
            rslt &= False
        if self.options.exit_check is None:
            self._add_message("Exit Check must not be None!")
            rslt &= False
        elif not isinstance(self.options.exit_check, str):
            self._add_message("Exit Check must be type str!")
            rslt &= False
        elif self.options.exit_check not in definitions.EXIT_CRITERIA_STRINGS:
            self._add_message(
                "Invalid value of Exit Check: {0}. Allowed values: {1}".format(
                    self.options.exit_check,
                    self._get_allowed_values(definitions.EXIT_CRITERIA_STRINGS),
                )
            )
            rslt &= False
        if self.options.chromosome_mutation == definitions.CROSS_DIVERSITY:
            if self.options.cross_diversity_mutation_gene_sampling is None:
                self._add_message(
                    "Cross Diversity Mutation Gene Selection must not be None!"
                )
                rslt &= False
            elif not isinstance(
                self.options.cross_diversity_mutation_gene_sampling, str
            ):
                self._add_message(
                    "Cross Diversity Mutation Gene Selection must be type str!"
                )
                rslt &= False
            elif not self._validate_selection(
                self.options.cross_diversity_mutation_gene_sampling,
                "Cross Diversity Mutation Gene Selection",
                self.options.number_of_mutation_genes,
                "Group Size for Cross Diversity Mutation Gene Selection must be below\
                    or equal than the number of mutation genes!",
            ):
                rslt &= False
        if self.options.logging is None:
            self._add_message("Logging must not be None!")
            rslt &= False
        elif not isinstance(self.options.logging, bool):
            self._add_message("Logging must be type bool!")
            rslt &= False
        if self.options.must_mutate_for_same_parents is None:
            self._add_message("Must Mutate For Same Parents must not be None!")
            rslt &= False
        elif not isinstance(self.options.must_mutate_for_same_parents, bool):
            self._add_message("Must Mutate For Same Parents must be type bool!")
            rslt &= False
        if (
            self.options.population_mutation == definitions.COST_DIVERSITY
            or definitions.PARENT_DIVERSITY in self.options.population_mutation
        ):
            if self.options.parent_diversity_mutation_chromosome_sampling is None:
                self._add_message(
                    "Parent Diversity Mutation Chromosome Sampling must not be None!"
                )
                rslt &= False
            elif not isinstance(
                self.options.parent_diversity_mutation_chromosome_sampling, str
            ):
                self._add_message(
                    "Parent Diversity Mutation Chromosome Sampling must be type str!"
                )
                rslt &= False
            elif not self._validate_selection(
                self.options.parent_diversity_mutation_chromosome_sampling,
                "Parents Diversity Mutation Chromosome Sampling",
                round(population_size * (keep_elitism_percentage / 100)) - self.options.immigration_number,  # type: ignore
                "Group Size for Parents Diversity Mutation Chromosome\
                Sampling cannot have the value below half population!",
            ):
                rslt &= False
        if self.options.population_mutation is None:
            self._add_message("Population Mutation must not be None!")
            rslt &= False
        elif not isinstance(self.options.population_mutation, str):
            self._add_message("Population Mutation must be type str!")
            rslt &= False
        elif definitions.PARAM_SEPARATOR in self.options.population_mutation:
            mutator_strings = [
                ms.strip()
                for ms in self.options.population_mutation.split(
                    definitions.PARAM_SEPARATOR
                )
            ]
            for mutator_string in mutator_strings:
                if mutator_string not in definitions.POPULATION_MUTATION_STRINGS:
                    self._add_message(
                        "Invalid value of Population Mutation:\
                            {0}. Allowed values: {1}".format(
                            mutator_string,
                            self._get_allowed_values(
                                definitions.POPULATION_MUTATION_STRINGS
                            ),
                        )
                    )
                    rslt &= False
        elif (
            self.options.population_mutation
            not in definitions.POPULATION_MUTATION_STRINGS
        ):
            self._add_message(
                "Invalid value of Population Mutation: {0}. Allowed values: {1}".format(
                    self.options.population_mutation,
                    self._get_allowed_values(definitions.POPULATION_MUTATION_STRINGS),
                )
            )
            rslt &= False
        if self.options.gene_mutation is None:
            self._add_message("Gene Mutation must not be None!")
            rslt &= False
        elif not isinstance(self.options.gene_mutation, str):
            self._add_message("Gene Mutation must be type str!")
            rslt &= False
        elif definitions.PARAM_SEPARATOR in self.options.gene_mutation:
            mutator_strings = [
                ms.strip()
                for ms in self.options.gene_mutation.split(definitions.PARAM_SEPARATOR)
            ]
            for mutator_string in mutator_strings:
                if mutator_string not in definitions.GENE_MUTATION_STRINGS:
                    self._add_message(
                        "Invalid value of Gene Mutation:\
                            {0}. Allowed values: {1}".format(
                            mutator_string,
                            self._get_allowed_values(definitions.GENE_MUTATION_STRINGS),
                        )
                    )
                    rslt &= False
        elif self.options.gene_mutation not in definitions.GENE_MUTATION_STRINGS:
            self._add_message(
                "Invalid value of Gene Mutation: {0}. Allowed values: {1}".format(
                    self.options.gene_mutation,
                    self._get_allowed_values(definitions.GENE_MUTATION_STRINGS),
                )
            )
            rslt &= False
        if self.options.parent_selection is None:
            self._add_message("Parent Selection must not be None!")
            rslt &= False
        elif not isinstance(self.options.parent_selection, str):
            self._add_message("Parent Selection must be type str!")
            rslt &= False
        elif not self._validate_selection(
            self.options.parent_selection,
            "Parent Selection",
            round(population_size * (keep_elitism_percentage / 100)) - self.options.immigration_number,  # type: ignore
            "Group Size for parent selection cannot have\
            the value below half population!",
        ):
            rslt &= False
        if self.options.requested_cost is None:
            self._add_message("Requested Cost must not be None!")
            rslt &= False
        elif not isinstance(self.options.requested_cost, float):
            self._add_message("Requested Cost must be type float!")
            rslt &= False
        if self.options.timeout is None:
            self._add_message("Timeout must not be None!")
            rslt &= False
        elif not isinstance(self.options.timeout, int):
            self._add_message("Timeout must be type int!")
            rslt &= False
        elif self.options.timeout < 1:
            self._add_message(
                "Invalid timeout value: {0}".format(str(self.options.timeout))
            )
            rslt &= False
        return rslt

    def _validate_selection(
        self,
        selection_string,
        selection_type,
        comparing_number,
        group_size_error_message,
    ) -> bool:
        selection_strings = selection_string.split(definitions.PARAM_SEPARATOR)
        if len(selection_strings) > 2 or (
            len(selection_strings) > 1
            and selection_strings[0] != definitions.TOURNAMENT
        ):
            self._add_message(
                "Invalid {0} value: {1}".format(selection_type, selection_string)
            )
            return False
        if (
            selection_strings[0] == definitions.TOURNAMENT
            and len(selection_strings) > 1
        ):
            group_size = selection_strings[1]
            n_group_size = -1
            try:
                n_group_size = int(group_size)
            except Exception:
                self._add_message(
                    "Invalid {0} value: {1}".format(selection_type, selection_string)
                )
                return False
            if n_group_size < 2:
                self._add_message(
                    "Invalid {0} value: {1}. Minimal group size is 2.".format(
                        selection_type, selection_string
                    )
                )
                return False
            if not isinstance(n_group_size, int):
                self._add_message(
                    "Invalid value for {0}: {1}".format(
                        selection_type, selection_string
                    )
                )
                return False
            elif int(n_group_size) > comparing_number:
                self._add_message(group_size_error_message)
                return False
        if selection_strings[0] not in definitions.SELECTION_STRINGS:
            self._add_message(
                "Invalid {0} value: {1}. Allowed values: {2}".format(
                    selection_type,
                    selection_string,
                    self._get_allowed_values(definitions.SELECTION_STRINGS),
                )
            )
            return False
        return True

    def _get_allowed_values(self, s_list):
        rslt = ""
        for s in s_list:
            rslt += s + ", "
        return rslt[:-2]

"""
The main genetic algorithm module
"""

import sys
from typing import List, Optional

import gadapt.ga_model.definitions as definitions
import gadapt.utils.ga_utils as ga_utils
from gadapt.adapters.validation.common_options_validator import CommonOptionsValidator
from gadapt.execution.ga_executor import GAExecutor
from gadapt.factory.ga_base_factory import BaseGAFactory
from gadapt.factory.ga_factory import GAFactory
from gadapt.ga_model.gene import Gene
from gadapt.ga_model.ga_options import GAOptions
from gadapt.ga_model.ga_results import GAResults
import copy


class GA:
    """
    The main genetic algorithm class
    """

    def __init__(
        self,
        cost_function=None,
        population_size=32,
        keep_elitism_percentage=50,
        number_of_crossover_parents=-1,
        exit_check=definitions.AVG_COST,
        requested_cost=sys.float_info.max,
        number_of_generations=200,
        max_attempt_no=2,
        parent_selection=definitions.ROULETTE_WHEEL,
        crossover=definitions.BLENDING,
        population_mutation="{0}{1}{2}{3}{4}".format(
            definitions.COST_DIVERSITY,
            definitions.PARAM_SEPARATOR,
            definitions.CROSS_DIVERSITY,
            definitions.PARAM_SEPARATOR,
            definitions.PARENT_DIVERSITY,
        ),
        number_of_mutation_chromosomes=-1,
        percentage_of_mutation_chromosomes=50.0,
        parent_diversity_mutation_chromosome_sampling=definitions.ROULETTE_WHEEL,
        must_mutate_for_same_parents=True,
        chromosome_mutation=f"{definitions.CROSS_DIVERSITY}{definitions.PARAM_SEPARATOR}{definitions.RANDOM}",
        gene_mutation=f"{definitions.CROSS_DIVERSITY}{definitions.PARAM_SEPARATOR}{definitions.RANDOM}",
        number_of_mutation_genes=-1,
        percentage_of_mutation_genes=20.0,
        cross_diversity_mutation_gene_sampling=definitions.ROULETTE_WHEEL,
        immigration_number=0,
        logging=False,
        timeout=600,
        factory: Optional[BaseGAFactory] = None,
    ) -> None:
        """
        The constructor of the GA class accepts all parameters required to
        create an instance of the GA class. It validates such parameters.

        Args:
            cost_function: Custom function for the cost calculation (fitness).
            The optimisation
            goal is minimising the output of the cost function.
                cost_function must be the function with one argument - a dictionary of
                values, where the key is an index (the ordinal of adding parameters)
                and the key is the parameter's value to be optimised.

                When adding parameters, there should be as
                many parameters as the function uses. The
                cost_function is the only mandatory parameter.

            population_size: Number of chromosomes in the population.

            exit_check: A criteria for the exit for the genetic algorithm

            requested_cost: This parameter only takes place when exit_check
            has value “requested”. It determines the requested value
            which causes the exit from the genetic algorithm

            number_of_generations: This parameter only takes place when exit_check
            has value “generations”. It determines the number of generations
            after which the genetic algorithm exits

            max_attempt_no: This parameter only takes place when exit_check
            has value “avg_cost” or “min_cost”. It determines the number of
            generations in which there is no improvement in the average/minimal cost.

            parent_selection: The sampling algorithm in parent selection.

            population_mutation: A type of mutation for the entire population.

                Based on the value of this parameter, the number of mutation
                chromosomes can be determined, along with how
                chromosomes for the mutation will be selected.

            number_of_mutation_chromosomes: The number of
            mutation chromosomes in the population.

                In case it's value is equal to or higher than 0,
                it overrides percentage_of_mutation_chromosomes.

                This value is the upper bound - the actual
                number of mutated chromosomes
                can vary from 1 to number_of_mutation_chromosomes.

            percentage_of_mutation_chromosomes: The percentage of mutated chromosomes
            in the population.
                This value is applied to the population_size value and rounded to an
                integer value, giving the number of mutation chromosomes.

                For example, if population_size has a value of 32,
                and percentage_of_mutation_chromosomes has a value of
                10, the number of mutation chromosomes will be 3.

                The calculated value is an upper bound - the actual
                number of mutated chromosomes can vary from 1 to the calculated value.

                percentage_of_mutation_chromosomes only applies if
                number_of_mutation_chromosomes does not have a valid
                integer value equal to or higher than 0.

            parent_diversity_mutation_chromosome_sampling: The
            sampling algorithm for mutating chromosomes when population_mutation
            contains value “parent_diversity”.
                It only applies when population_mutation has value
                “parent_diversity”. It determines the way how chromosomes are to
                be selected based on the diversity of their parents.

            must_mutate_for_same_parents: Indicates if completely the same
            parents must influence mutation for their children.
                In other words, each child will be mutated if it has
                parents with a diversity value of 0.

                If must_mutate_for_same_parents has the value True, the
                number of mutated chromosomes can outreach value
                determined by number_of_mutation_chromosomes or
                percentage_of_mutation_chromosomes

            chromosome_mutation: The type of mutation of genes in chromosomes.

            gene_mutation: The type of assigning values to genes in the mutation

            number_of_mutation_genes: The number of mutated genes in each chromosome.
                In case it's value is equal to or higher than 0, it overrides
                percentage_of_mutation_genes.

                This value is the upper bound - the number of mutated genes
                can vary from 1 to number_of_mutation_genes.

            percentage_of_mutation_genes: The percentage of
            mutated genes in each chromosome.
                It applies to the chromosome size
                (number of genes in each chromosome), and
                the calculated value rounds to an integer value.

                The calculated value is the upper bound - the actual number of
                mutated genes can vary from 1 to the calculated value.

                percentage_of_mutation_genes only applies if
                number_of_mutations_genes does not have a valid
                integer value equal to or higher than 0.

            cross_diversity_mutation_gene_sampling: The sampling algorithm for
            mutating chromosomes when chromosome_mutation has value “cross_diversity”.
                It only applies when chromosome_mutation has value
                “cross_diversity” . It determines the way how genes
                are to be selected based on the cross-diversity.

            immigration_number: Refers to the “Random Immigrants”
            concepts. This strategy introduces a certain number of
            individuals into the population during the evolution process.
                These new individuals are generated randomly
                and injected into the population.

            logging: If this parameter has a True value, the log file
            will be created in the current working directory.
            The log file contains the flow of genetic algorithm execution,
            along with values of chromosomes, genes and cost
            functions in each generation

            timeout: A number of seconds after which the genetic algorithm
            optimisation will exit, regardless of whether
            exit_check criteria is reached.

            factory: Factory for creating object
        """
        self.cost_function = cost_function
        self.population_size = population_size
        self.keep_elitism_percentage = keep_elitism_percentage
        self.number_of_crossover_parents = number_of_crossover_parents
        self.exit_check = exit_check
        self.requested_cost = requested_cost
        self.number_of_generations = number_of_generations
        self.max_attempt_no = max_attempt_no
        self.parent_selection = parent_selection
        self.crossover = crossover
        self.population_mutation = population_mutation
        self.must_mutate_for_same_parents = must_mutate_for_same_parents
        self.number_of_mutation_chromosomes = number_of_mutation_chromosomes
        self.percentage_of_mutation_chromosomes = percentage_of_mutation_chromosomes
        self.number_of_mutation_genes = number_of_mutation_genes
        self.percentage_of_mutation_genes = percentage_of_mutation_genes
        self.chromosome_mutation = chromosome_mutation
        self.gene_mutation = gene_mutation
        self.immigration_number = immigration_number
        self.logging = logging
        self._genes: List[Gene] = []
        self.cross_diversity_mutation_gene_sampling = (
            cross_diversity_mutation_gene_sampling
        )
        self.parent_diversity_mutation_chromosome_sampling = (
            parent_diversity_mutation_chromosome_sampling
        )
        self.timeout = timeout
        self._current_dv_id = 0
        self._factory = factory

    def execute(self) -> GAResults:
        """
        Executes genetic algorithm optimization base on the
        provided parameters and arguments.
        """
        validator = CommonOptionsValidator(self)
        validator.validate()
        if not validator.success:
            results = GAResults()
            results.success = False
            results.messages = validator.validation_messages
            return results
        ga_options = GAOptions(self)
        factory: BaseGAFactory = self.get_factory()
        factory.initialize_factory(self.clone())
        return GAExecutor(ga_options, factory).execute()

    def get_factory(self) -> BaseGAFactory:
        if self._factory:
            return self._factory
        return GAFactory()

    @property
    def population_size(self) -> int:
        """
        Population size number
        """
        return self._population_size

    @population_size.setter
    def population_size(self, value: int):
        self._population_size = ga_utils.try_get_int(value)

    @property
    def keep_elitism_percentage(self) -> int:
        """
        Percentage number of chromosomes to be kept in the population by the cost value
        """
        return self._keep_elitism_percentage

    @keep_elitism_percentage.setter
    def keep_elitism_percentage(self, value: int):
        self._keep_elitism_percentage = ga_utils.try_get_int(value)

    @property
    def number_of_crossover_parents(self) -> int:
        """
        Number of parents to be included in the mating pool
        """
        return self._number_of_crossover_parents

    @number_of_crossover_parents.setter
    def number_of_crossover_parents(self, value: int):
        self._number_of_crossover_parents = ga_utils.try_get_int(value)

    def add(
        self,
        min_value: float = -sys.float_info.max,
        max_value: float = sys.float_info.max,
        step: float = sys.float_info.min,
    ):
        """
        Adds variables to be optimized.
        Args:
            min_value (float): lower bound of possible variable values
            max_value (float): upper bound of possible variable values
            step (float): the step that will be used in changing the
            variables values during the optimization
        """
        if step < 0.000000000000001:
            step = 0.000000000000001
        if (not isinstance(min_value, float) and not isinstance(min_value, int)) or (
            not isinstance(max_value, float) and not isinstance(max_value, int)
        ):
            raise Exception("min value, max value and step must be numerical values!")
        gene = Gene(self._current_dv_id)
        gene.min_value = min_value
        gene.max_value = max_value
        gene.step = step
        self._genes.append(gene)
        self._current_dv_id += 1

    @property
    def cost_function(self):
        """
        Custom function for the cost calculation (fitness). The optimisation goal
        is minimising the output of the cost function.
        cost_function must be the function with one argument -
        a dictionary of values, where the key is an index
        (the ordinal of adding parameters)
        and the key is the parameter's value to be optimised.
        When adding parameters, there should be as many parameters
        as the function uses. The cost_function is the
        only mandatory parameter.
        """
        return self._cost_function

    @cost_function.setter
    def cost_function(self, value):
        self._cost_function = value

    @property
    def number_of_mutation_genes(self) -> int:
        """
        The number of mutated genes in each chromosome.
        In case it's value is equal to or higher than 0, it overrides
        percentage_of_mutation_genes.
        This value is the upper bound - the number of mutated genes
        can vary from 1 to number_of_mutation_genes.
        """
        return self._number_of_mutation_genes

    @number_of_mutation_genes.setter
    def number_of_mutation_genes(self, value: int):
        self._number_of_mutation_genes = ga_utils.try_get_int(value)

    @property
    def percentage_of_mutation_genes(self) -> float:
        """
        The percentage of mutated genes in each chromosome.
        It applies to the chromosome size (number of genes in each chromosome),
        and the calculated value rounds to an integer value.
        The calculated value is the upper bound - the actual number of mutated
        genes can vary from 1 to the calculated value.
        percentage_of_mutation_genes only applies if number_of_mutations_genes
        does not have a valid integer value equal to or higher than 0.
        """
        return self._percentage_of_mutation_genes

    @percentage_of_mutation_genes.setter
    def percentage_of_mutation_genes(self, value: float):
        self._percentage_of_mutation_genes = ga_utils.try_get_float(value)

    @property
    def number_of_mutation_chromosomes(self) -> int:
        """
        The number of mutation chromosomes in the population.
        In case it's value is equal to or higher than 0, it
        overrides percentage_of_mutation_chromosomes.
        This value is the upper bound - the actual number of
        mutated chromosomes can vary from 1 to number_of_mutation_chromosomes.
        """
        return self._number_of_mutation_chromosomes

    @number_of_mutation_chromosomes.setter
    def number_of_mutation_chromosomes(self, value: int):
        self._number_of_mutation_chromosomes = ga_utils.try_get_int(value)

    @property
    def percentage_of_mutation_chromosomes(self) -> float:
        """
        The percentage of mutated chromosomes in the population.

        This value is applied to the population_size value and
        rounded to an integer value, giving the number
        of mutation chromosomes.

        For example, if population_size has a value of 32, and
        percentage_of_mutation_chromosomes has a value of 10,
        the number of mutation chromosomes will be 3.

        The calculated value is an upper bound - the actual number of
        mutated chromosomes can vary from 1 to the calculated value.
        percentage_of_mutation_chromosomes only applies
        if number_of_mutation_chromosomes
        does not have a valid integer value equal to or higher than 0.
        """
        return self._percentage_of_mutation_chromosomes

    @percentage_of_mutation_chromosomes.setter
    def percentage_of_mutation_chromosomes(self, value: float):
        self._percentage_of_mutation_chromosomes = ga_utils.try_get_float(value)

    @property
    def immigration_number(self) -> int:
        """
        Refers to the “Random Immigrants” concepts. This strategy introduces
        a certain number of individuals into the population
        during the evolution process.
        """
        return self._immigration_number

    @immigration_number.setter
    def immigration_number(self, value: int):
        self._immigration_number = ga_utils.try_get_int(value)

    @property
    def population_mutation(self) -> str:
        """
        A type of mutation for the entire population.

        Supported values:

        **"cost_diversity"** - It applies to the number of mutation chromosomes.
        “cost_diversity” determines the number of mutated chromosomes adaptively,
        using the diversity of costs in the population. Lower cost diversity
        means a higher number of mutated chromosomes. The minimal value of
        mutated chromosomes is 0, and the maximal value is determined by
        the value of number_of_mutation_chromosomes or
        percentage_of_mutation_chromosomes
        parameters. If population_mutation has a value other than
        “cost_diversity”, the number of mutation chromosomes is a
        random value from 1 to number_of_mutation_chromosomes
        value (or to value determined by percentage_of_mutation_chromosomes value).
        “cost_diversity” means that the “parent_diversity” method is selected
        to select chromosomes to be mutated. This method only determines
        the number of mutated chromosomes, but not how
        chromosomes are selected for the mutation.

        **"parent_diversity"** - It applies to the way how mutation
        chromosomes will be selected. “parent_diversity” selects
        chromosomes to be mutated using the diversity of their parents.
        The more similar parents (lower parent diversity) mean a higher
        probability of mutation for the child. Based on the calculated
        parent diversity, chromosomes may be selected by one of the
        sampling methods, which is determined by the value of the
        parent_diversity_mutation_chromosome_sampling parameter.

        **"random"** - It applies to the number of mutation chromosomes
        and to the way how mutation chromosomes will be selected. “random”
        selects chromosomes to be mutated randomly, and randomly
        determines the number of mutated chromosomes (with the
        upper bound of number_of_mutation_chromosomes)
        """
        return self._population_mutation

    @population_mutation.setter
    def population_mutation(self, value: str):
        self._population_mutation = ga_utils.prepare_string(value)

    @property
    def parent_diversity_mutation_chromosome_sampling(self) -> str:
        """
        The sampling algorithm for mutating chromosomes when
        population_mutation contains value “parent_diversity”.
        It only applies when population_mutation has value
        “parent_diversity”. It determines the way how chromosomes are
        to be selected based on the diversity of their parents.

        Supported values:

        **"roulette_wheel"** - The Roulette Wheel sampling algorithm
        (also known as “Weighted Random Pairing”). The probabilities
        assigned to the chromosomes to be mutated are proportional
        to the similarity of their parents (inversely proportional
        to the parent diversity). A chromosome with the lowest
        parent diversity has the greatest probability of
        mutation, while the chromosome with the highest
        parent diversity has the lowest probability of mutation.

        **"tournament"** - The Tournament sampling algorithm.
        It randomly picks small subsets (groups) of chromosomes,
        and chromosomes with the lowest parent diversity (highest parent similarity)
        in subsets are chosen to be mutated. “tournament” can have an additional
        parameter separated from the “tournament” keyword by the comma.
        The other value represents a group size. For example, “tournament,8” means
        that the tournament mutation sampling algorithm is chosen, and
        each group contains up to 8 members. The default group size is 4.

        **"from_top_to_bottom"** - From Top To Bottom sampling
        algorithm starts at the top of the list and
        selects chromosomes for mutation.

        **"random"** - Random selection algorithm uses a
        uniform random number generator to select
        chromosomes for mutation. In this case,
        sampling for mutation will not depend
        on parent diversity.
        """
        return self._parent_diversity_mutation_chromosome_sampling

    @parent_diversity_mutation_chromosome_sampling.setter
    def parent_diversity_mutation_chromosome_sampling(self, value: str):
        self._parent_diversity_mutation_chromosome_sampling = ga_utils.prepare_string(
            value
        )

    @property
    def chromosome_mutation(self) -> str:
        """
        The type of mutation of genes in chromosomes.

        Supported values:

        **"cross_diversity"** - Considers the diversity of genes of the same
        type in the population. Lower diversity can mean
        that this gene approaches some local
        minimums, and therefore such genes increase the
        chance for mutation. Based on the calculated
        cross-diversity, chromosomes may be selected by
        one of the sampling methods, which is
        determined by the value of the
        cross_diversity_mutation_gene_sampling parameter.

        **"random"** - Genes are randomly selected for the mutation
        """
        return self._chromosome_mutation

    @chromosome_mutation.setter
    def chromosome_mutation(self, value: str):
        self._chromosome_mutation = ga_utils.prepare_string(value)

    @property
    def gene_mutation(self) -> str:
        """
        Way of assigning the value to the gene

        Supported values:

        **"normal_distribution"** - assignes normally distributed random number to the variable selected for mutation

        **"random"** - Random values are assigned to genes
        """
        return self._gene_mutation

    @gene_mutation.setter
    def gene_mutation(self, value: str):
        self._gene_mutation = ga_utils.prepare_string(value)

    @property
    def cross_diversity_mutation_gene_sampling(self) -> str:
        """
        The sampling algorithm for mutating chromosomes when chromosome_mutation
        has value “cross_diversity”.
        It only applies when chromosome_mutation has value “cross_diversity” .
        It determines the way how genes are to be selected based on the cross-diversity.

        Supported values:

        **"roulette_wheel"** - The Roulette Wheel sampling algorithm
        (also known as “Weighted Random Pairing”). The probabilities
        assigned to the genes to be mutated are inversely
        proportional to their cross-diversity. A gene
        with the lowest cross-diversity has the greatest
        probability of mutation, while the gene with the
        highest cross-diversity has the lowest
        probability of mutation.

        **"tournament"** - The Tournament sampling algorithm. It randomly picks
        small subsets (groups) of genes, and genes with the lowest cross-diversity
        in subsets are chosen to be mutated. “tournament” can have
        an additional parameter separated from the “tournament”
        keyword by the comma. The other value represents a group size.
        For example, “tournament,3” means that the tournament
        mutation sampling algorithm is chosen, and each group
        contains up to 3 members. The default group size is 4.

        **"from_top_to_bottom"** - From Top To Bottom sampling
        algorithm starts at the top of the list and selects genes for mutation.

        **"random"** - Random sampling algorithm uses a
        uniform random number generator to select genes for mutation.
        In this case, sampling for the mutation will not
        depend on gene cross-diversity.
        """
        return self._cross_diversity_mutation_gene_sampling

    @cross_diversity_mutation_gene_sampling.setter
    def cross_diversity_mutation_gene_sampling(self, value: str):
        self._cross_diversity_mutation_gene_sampling = ga_utils.prepare_string(value)

    @property
    def max_attempt_no(self) -> int:
        """
        This parameter only takes place when exit_check has value “avg_cost”
        or “min_cost”. It determines the number of generations
        in which there is no improvement in the average/minimal cost.
        """
        return self._max_attempt_no

    @max_attempt_no.setter
    def max_attempt_no(self, value: int):
        self._max_attempt_no = ga_utils.try_get_int(value)

    @property
    def exit_check(self) -> str:
        """
        A criteria for the exit for the genetic algorithm.

        Supported values:

        **"avg_cost"** - The optimisation exit is triggered when the
        average cost of the upper half of the population
        is not improved in the specified number of generations

        **"min_cost"** - The optimisation exit is triggered when the minimal cost
        in the population is not improved in the specified number of generations

        **"requested"** - The optimisation exit is triggered when the
        requested value reached
        """
        return self._exit_check

    @exit_check.setter
    def exit_check(self, value: str):
        self._exit_check = ga_utils.prepare_string(value)

    @property
    def number_of_generations(self) -> float:
        """
        This parameter only takes place when exit_check
        has value “generations”. It determines the number of generations
        after which the genetic algorithm exits
        """
        return self._number_of_generations

    @number_of_generations.setter
    def number_of_generations(self, value: float):
        self._number_of_generations = ga_utils.try_get_float(value)

    @property
    def parent_selection(self) -> str:
        """
        The algorithm for sampling algorithm in parent selection.

        Supported values:

        **"roulette_wheel"** - Roulette Wheel sampling algorithm
        (also known as “Weighted Random Pairing”).
        The probabilities assigned to the chromosomes in the mating pool are
        inversely proportional to their cost. A chromosome with the lowest
        cost has the greatest probability of mating, while the chromosome
        with the highest cost has the lowest probability of mating.

        **"tournament"** - Tournament sampling algorithm. It randomly picks small
        subsets (groups) of chromosomes from the mating pool, and chromosomes
        with the lowest cost in subsets become a parent. “tournament”
        can have an additional parameter separated from the “tournament”
        keyword by the comma. The other value represents a group size.
        For example, “tournament,8” means that the tournament
        sampling algorithm for parent selection is chosen, and
        each group contains up to 8 members.
        The default group size is 4.

        **"from_top_to_bottom"** - From Top To Bottom sampling
        algorithm starts at the top of
        the list and pairs the chromosomes two at a time until the top kept chromosomes
        are selected for mating. Thus, the algorithm pairs odd rows with even rows.

        **"random"** - Random sampling algorithm uses a uniform random
        number generator to select chromosomes.
        """
        return self._parent_selection

    @parent_selection.setter
    def parent_selection(self, value: str):
        self._parent_selection = ga_utils.prepare_string(value)

    @property
    def crossover(self) -> str:
        """
        The crossover algorithm

        Supported values:

        **"blending"** - combines gene values from the two parents into new variable values in offsprings.
        One value of the offspring variable comes from a combination of the two
        corresponding values of the parental genes

        **"uniform"** - Genes from parents' chromosomes are combined in a uniform way.
        """
        return self._crossover

    @crossover.setter
    def crossover(self, value: str):
        self._crossover = ga_utils.prepare_string(value)

    @property
    def requested_cost(self) -> float:
        """
        This parameter only takes place when exit_check has value “requested”.
        It determines the requested value which causes the
        exit from the genetic algorithm
        """
        return self._requested_cost

    @requested_cost.setter
    def requested_cost(self, value: float):
        self._requested_cost = ga_utils.try_get_float(value)

    @property
    def logging(self) -> bool:
        return self._logging

    @logging.setter
    def logging(self, value: bool):
        """
        If this parameter has a True value, the log file will
        be created in the current working directory.
        The log file contains the flow of genetic algorithm execution,
        along with values of chromosomes, genes and
        cost functions in each generation
        """
        self._logging = ga_utils.try_get_bool(value)

    @property
    def must_mutate_for_same_parents(self) -> bool:
        """
        Indicates if completely the same parents must influence
        mutation for their children.
        In other words, each child will be mutated if it has parents
        with a diversity value of 0.
        If must_mutate_for_same_parents has the value True, the number of
        mutated chromosomes can outreach value determined
        by number_of_mutation_chromosomes
        or percentage_of_mutation_chromosomes
        """
        return self._must_mutate_for_same_parents

    @must_mutate_for_same_parents.setter
    def must_mutate_for_same_parents(self, value: bool):
        self._must_mutate_for_same_parents = ga_utils.try_get_bool(value)

    @property
    def timeout(self) -> int | str:
        """
        A number of seconds after which the genetic algorithm optimisation will\
            exit, regardless of whether exit_check criteria is reached.
        """
        return self._timeout

    @timeout.setter
    def timeout(self, value: int | str) -> None:
        self._timeout = ga_utils.try_get_int(value)

    def clone(self):
        # Create a new instance of the class
        new_instance = self.__class__.__new__(self.__class__)

        # Copy the attributes from the current instance to the new instance
        new_instance.__dict__ = copy.deepcopy(self.__dict__)

        return new_instance

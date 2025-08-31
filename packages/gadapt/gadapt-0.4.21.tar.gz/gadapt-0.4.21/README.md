# GAdapt: Self-Adaptive Genetic Algorithm

A comprehensive and customizable genetic algorithm library.

## Table of Contents
- [Introduction](#introduction)
  - [What Innovations Does GAdapt Bring?](what-innovations-does-gadapt-bring)
- [Installation](#installation)
- [Releases](#releases)
- [Source code](#source-code)
- [API Documentation](#api-documentation)
- [Usage](#usage)
  - [Parameter Settings](#parameter-settings)
  - [Parameters Description](#parameters-description)
  - [Adding Variables](#adding-variables)
  - [GA Execution and Optimisation Results](#ga-execution-and-optimisation-results)
- [GA Customisation](#ga-customisation)

## Introduction

[GAdapt](https://gadapt.com) is an open-source Python library for Genetic Algorithm optimization. It implements innovative concepts for adaptive mutation of genes and chromosomes.

### What Innovations Does GAdapt Bring?

**GAdapt** introduces self-adaptive determination of how many and which chromosomes and genes will be mutated. In addition, it determines the gene alteration type. This determination is based on the diversity of parents, diversity of cost, and cross-diversity of genes in the population. The higher diversity and lower convergence necessitate fewer mutated chromosomes. A high diversity level also allows for more mutated genes within each chromosome. At this stage, gene value alterations are encouraged to be unbiased, favoring a uniform distribution of values. This approach ensures that mutations are not overly frequent, but selected chromosomes can undergo significant changes, promoting the exploration of potential solutions. As diversity decreases and convergence increases, the frequency of mutated chromosomes rises, the number of mutated genes inside chromosomes decreases, and gene value changes are biased towards previously attained values, encouraging greater exploitation and fine-tuning of existing solutions. Throughout this process, the selection of mutated chromosomes and gene values should prioritize those with lower diversity and higher convergence levels, maintaining exploration and preventing GA from getting stuck in some local optimums.

The proposed method refines mutation selection, rate determination, and alteration processes, potentially surpassing the limitations of traditional mutation techniques and opening up new possibilities for significantly improved GA performance.

## Installation

To install **GAdapt**, use **pip** with the following command:

```bash
pip install gadapt
```

## Releases
The latest releases of GAdapt can be found at the PyPI repository: [GAdapt on PyPI](https://pypi.org/project/gadapt/)

## Source Code
The source code is available on GitHub: [GAdapt on GitHub](https://github.com/bpzoran/gadapt/)

## API Documentation
For detailed API documentation, refer to: [GAdapt API Documentation](https://www.gadapt.com/api/)

## Usage
Below is an example optimizing variable values for a complex trigonometric function:
```python
from gadapt.ga import GA
import math

#trigonometric function definition
def trig_func(args):    
    return math.sqrt(abs(math.cos(args[0]))) + math.pow(math.cos(args[1]), 2) + math.sin(args[2]) + math.pow(args[3], 2) + math.sqrt(args[4]) + math.cos(args[5]) - (args[6]*math.sin(pow(args[6], 3)) + 1) + math.sin(args[0]) / (math.sqrt(args[0])/3 + (args[6]*math.sin(pow(args[6], 3)) + 1) ) / math.sqrt(args[4]) + math.cos(args[5])

#Instantiation of genetic algorithm for desired function
ga = GA(cost_function=trig_func)

#Adding variables (minimal value, maximal value and step)
ga.add(1.0, 4.0, 0.01)
ga.add(37.0, 40.0, 0.01)
ga.add(78.0, 88.0, 0.1)
ga.add(-5.0, 4.0, 0.1)
ga.add(1.0, 100.0, 1)
ga.add(1.0, 4.0, 0.01)
ga.add(-1, -0.01, 0.005)

#Execution of the genetic algorithm
results = ga.execute()

#Printing results
print(results)
```

The possible output:
```
Min cost: -3.370583074871819
Number of iterations: 286
Parameter values:
0: 1.57
1: 39.27
2: 86.4
3: 0.0
4: 1.0
5: 3.14
6: -1.0
```

In this example, the genetic algorithm searches for the combination of seven parameters, bringing the lowest value for the passed function. The only mandatory attribute to the genetic algorithm is *cost_function*, and other attributes in this example took default values. Parameters to be optimized are added by the "add" method. There are seven parameters to be optimized in this example.
### Parameter Settings
GAdapt genetic algorithm can receive parameters through constructor, properties, or a combination of both. Below are the supported parameters:

Passing parameters through the class constructor:
```python
ga = GA(cost_function=trig_func,
    population_size=32,
    population_mutation="cost_diversity,parent_diversity",
    number_of_mutation_chromosomes=6,
    number_of_mutation_genes=2,
    exit_check="min_cost",
    max_attempt_no=20,
    logging=True,
    timeout=3600)
```
Passing parameters through the class properties:
```python
ga = GA()
ga.cost_function = trig_func
population_size=32
ga.population_mutation="cost_diversity,parent_diversity"
ga.number_of_mutation_chromosomes=6
ga.number_of_mutation_genes=2
ga.exit_check="min_cost"
ga.max_attempt_no=20
ga.logging=True
ga.timeout=3600
```
Passing parameters through the class constructor and properties:
```python
ga = GA(cost_function=trig_func, population_size=32)
ga.population_mutation="cost_diversity,parent_diversity"
ga.number_of_mutation_chromosomes=6
ga.number_of_mutation_genes=2
ga.exit_check="min_cost"
ga.max_attempt_no=20
ga.logging=True
ga.timeout=3600
```
### Parameters Description
**cost_function**=*None* - Custom function for the cost calculation (fitness). The optimisation goal is minimising the output of the cost function. *cost_function* must be the function with one argument - a dictionary of values, where the key is an index (the ordinal of adding parameters) and the key is the parameter's value to be optimised. When adding parameters, there should be as many parameters as the function uses. The *cost_function* is the only mandatory parameter.

**population_size**=*32* - Number of chromosomes in the population.

**exit_check**=*"avg_cost"* - A criteria for the exit for the genetic algorithm.  
Supported values:
- *"avg_cost"* - The optimisation exit is triggered when the average cost of the upper half of the population is not improved in the specified number of generations  
- *"min_cost"* - The optimisation exit is triggered when the minimal cost in the population is not improved in the specified number of generations  
- *"requested"* - The optimisation exit is triggered when the requested value reached
- *"generations"* - The optimisation exit requested number of generations defined by "number_of_generations" parameter is reached
    
**max_attempt_no**=*2* - This parameter only takes place when *exit_check* has value *"avg_cost"* or *"min_cost"*. It determines the number of generations in which there is no improvement in the average/minimal cost.

**requested_cost**=*sys.float_info.max* - This parameter only takes place when *exit_check* has value *"requested"*. It determines the requested value which causes the exit from the genetic algorithm

**number_of_generations**=*200* - This parameter only takes place when exit_check has value “generations”. It determines the number of generations after which the genetic algorithm exits

**timeout**=*120* - A number of seconds after which the genetic algorithm optimisation will exit, regardless of whether *exit_check* criteria is reached.

**parent_selection**=*"roulette_wheel"* - The algorithm for parent selection.  
Supported values:
- *"roulette_wheel"* - Roulette Wheel selection algorithm (also known as "Weighted Random Pairing"). The probabilities assigned to the chromosomes in the mating pool are inversely proportional to their cost. A chromosome with the lowest cost has the greatest probability of mating, while the chromosome with the highest cost has the lowest probability of mating.  
- *"tournament"* - Tournament selection algorithm. It randomly picks small subsets (groups) of chromosomes from the mating pool, and chromosomes with the lowest cost in subsets become a parent. *"tournament"* can have an additional parameter separated from the *"tournament"* keyword by the comma. The other value represents a group size. For example, *"tournament,8"* means that the tournament parent selection algorithm is chosen, and each group contains up to 8 members. The default group size is 4.  
- *"from_top_to_bottom"* - From Top To Bottom selection algorithm starts at the top of the list and pairs the chromosomes two at a time until the top kept chromosomes are selected for mating. Thus, the algorithm pairs odd rows with even rows.  
- *"random"* - Random selection algorithm uses a uniform random number generator to select chromosomes.  

**crossover**=*"blending"* - The algorithm for parent selection. If the Parent Diversity mutation is used, blending crossover will be used, of the choice of this parameter.
Supported values:
- *"blending"* - Blending crossover combines gene values from the two parents into new variable values in offsprings. One value of the offspring variable comes from a combination of the two corresponding values of the parental genes  
- *"uniform"* - Uniform crossover combines chromosomes in a uniform way.
    
**percentage_of_mutation_chromosomes**=*50.0* - The percentage of mutated chromosomes in the population. This value is applied to the *population_size* value and rounded to an integer value, giving the number of mutation chromosomes. For example, if *population_size* has a value of 32, and *percentage_of_mutation_chromosomes* has a value of 10, the number of mutation chromosomes will be 3. The calculated value is an upper bound - the actual number of mutated chromosomes can vary from 1 to the calculated value. *percentage_of_mutation_chromosomes* only applies if *number_of_mutation_chromosomes* does not have a valid integer value equal to or higher than 0.

**number_of_mutation_chromosomes**=*-1* - The number of mutation chromosomes in the population. In case it's value is equal to or higher than 0, it overrides *percentage_of_mutation_chromosomes*. This value is the upper bound - the actual number of mutated chromosomes can vary from 1 to *number_of_mutation_chromosomes*.

**percentage_of_mutation_genes**=*20* - The percentage of mutated genes in each chromosome. It applies to the chromosome size (number of genes in each chromosome), and the calculated value rounds to an integer value. The calculated value is the upper bound - the actual number of mutated genes can vary from 1 to the calculated value. *percentage_of_mutations_genes* only applies if *number_of_mutations_genes* does not have a valid integer value equal to or higher than 0.

**number_of_mutation_genes**=*-1* - The number of mutated genes in each chromosome. In case it's value is equal to or higher than 0, it overrides *percentage_of_mutations_genes*. This value is the upper bound - the number of mutated genes can vary from 1 to *number_of_mutation_genes*.

**population_mutation**=*"cost_diversity,parent_diversity"* - A type of mutation for the entire population. Based on the value of this parameter, the number of mutation chromosomes can be determined, along with how chromosomes for the mutation will be selected.
Supported values:
- *"cost_diversity"* - It applies to the number of mutation chromosomes. *"cost_diversity"* determines the number of mutated chromosomes adaptively, using the diversity of costs in the population. Lower cost diversity means a higher number of mutated chromosomes. The minimal value of mutated chromosomes is 0, and the maximal value is determined by the value of *number_of_mutation_chromosomes* or *percentage_of_mutation_chromosomes* parameters. If *population_mutation* has a value other than *"cost_diversity"*, the number of mutation chromosomes is a random value from 1 to *number_of_mutation_chromosomes* value (or to value determined by *percentage_of_mutation_chromosomes* value). *"cost_diversity"* means that the *"parent_diversity"* method is selected to select chromosomes to be mutated. This method only determines the number of mutated chromosomes, but not how chromosomes are selected for the mutation.  
- *"cross_diversity"* - It applies to the number of mutation chromosomes. Determines the number of mutated chromosomes based on dispersion of gene values. The lower dispersion indicates the higher number of mutated chromosomes. The minimal value of mutated chromosomes is 0, and the maximal value is determined by the value of *number_of_mutation_chromosomes* or *percentage_of_mutation_chromosomes* parameters.
- *"parent_diversity"* - It applies to the way how mutation chromosomes will be selected. *"parent_diversity"* selects chromosomes to be mutated using the diversity of their parents. The more similar parents (lower parent diversity) mean a higher probability of mutation for the child. Based on the calculated parent diversity, chromosomes may be selected by one of the selection methods, which is determined by the value of the *parent_diversity_mutation_chromosome_sampling* parameter.  
- *"random"* - It applies to the number of mutation chromosomes and to the way how mutation chromosomes will be selected. *"random"* selects chromosomes to be mutated randomly, and randomly determines the number of mutated chromosomes (with the upper bound of **number_of_mutation_chromosomes**)
- *"strict"* - It applies to the number of mutation chromosomes. The strict number of chromosomes will be mutated, determined by **number_of_mutation_chromosomes** parameter.

Population_mutation may have more values, separated by a comma. It means that more than one method can be chosen for the mutation of chromosomes in the population. For example, *"cost_diversity,parent_diversity"* means that number of mutation chromosomes will be determined by the cost diversity and the selection of chromosomes to be mutated will be defined by parent diversity. *"cost_diversity,random"* means that the cost diversity will determine the number of mutation chromosomes, and the selection of chromosomes to be mutated will be chosen randomly.
    
**parent_diversity_mutation_chromosome_sampling**=*"roulette_wheel"* - The selection algorithm for mutating chromosomes when *population_mutation* contains value *"parent_diversity"*. It only applies when *population_mutation* has value *"parent_diversity"*. It determines the way how chromosomes are to be selected based on the diversity of their parents.  
Supported values:
- *"roulette_wheel"* - The Roulette Wheel selection algorithm (also known as "Weighted Random Pairing"). The probabilities assigned to the chromosomes to be mutated are proportional to the similarity of their parents (inversely proportional to the parent diversity). A chromosome with the lowest parent diversity has the greatest probability of mutation, while the chromosome with the highest parent diversity has the lowest probability of mutation.  
- *"tournament"* - The Tournament selection algorithm. It randomly picks small subsets (groups) of chromosomes, and chromosomes with the lowest parent diversity (highest parent similarity) in subsets are chosen to be mutated. *"tournament"* can have an additional parameter separated from the *"tournament"* keyword by the comma. The other value represents a group size. For example, *"tournament,8"* means that the tournament mutation selection algorithm is chosen, and each group contains up to 8 members. The default group size is 4.  
- *"from_top_to_bottom"* - From Top To Bottom selection algorithm starts at the top of the list and selects chromosomes for mutation.  
- *"random"* - Random selection algorithm uses a uniform random number generator to select chromosomes for mutation. In this case, selection for mutation will not depend on parent diversity.  
    
**must_mutate_for_same_parents**=*True* - Indicates if completely the same parents must influence mutation for their children. In other words, each child will be mutated if it has parents with a diversity of value of 0. If *must_mutate_for_same_parents* has the value True, the number of mutated chromosomes can outreach value determined by *number_of_mutation_chromosomes* or *percentage_of_mutation_chromosomes*

**chromosome_mutation**=*"cross_diversity,random"* - The type of gene selection in chromosomes for mutation  
Supported values:
- *"cross_diversity"* - Considers the diversity of genes of the same type in the population. Lower diversity can mean that this gene approaches some local minimums, and therefore such genes increase the chance for mutation. Based on the calculated cross-diversity, chromosomes may be selected by one of the selection methods, which is determined by the value of the *cross_diversity_mutation_gene_sampling* parameter.  
- *"random"* - Genes are randomly selected for the mutation. Random number of genes for mutation is determined, up to *number_of_mutation_genes*
- *"strict"* - Strict number of genes will be mutated, determined by *number_of_mutation_genes* parameter.

**gene_mutation**=*"cross_diversity,random"* - The type of assigning mutated values to genes
Supported values:
- *"normal_distribution"* - assigns normally distributed random number to the variable selected for mutation
- *"cross_diversity"* - assigns normally distributed random number to the variable selected for mutation, with standard deviation based on the cross-diversity coefficient
- *"random"* - Random values are assigned to genes

**cross_diversity_mutation_gene_sampling**=*"roulette_wheel"* - the selection algorithm for mutating chromosomes when *chromosome_mutation* has value *"cross_diversity"*. It only applies when *chromosome_mutation* has value *"cross_diversity"* . It determines the way how genes are to be selected based on the cross-diversity.  
Supported values:
- *"roulette_wheel"* - The Roulette Wheel selection algorithm (also known as "Weighted Random Pairing"). The probabilities assigned to the genes to be mutated are inversely proportional to their cross-diversity. A gene value with the lowest cross-diversity has the greatest probability of mutation, while the gene with the highest cross-diversity has the lowest probability of mutation.  
- *"tournament"* - The Tournament selection algorithm. It randomly picks small subsets (groups) of genes, and genes with the lowest cross-diversity in subsets are chosen to be mutated. *"tournament"* can have an additional parameter separated from the *"tournament"* keyword by the comma. The other value represents a group size. For example, *"tournament,3"* means that the tournament mutation selection algorithm is chosen, and each group contains up to 3 members. The default group size is 4.  
- *"from_top_to_bottom"* - From Top To Bottom selection algorithm starts at the top of the list and selects genes for mutation.  
- *"random"* - Random selection algorithm uses a uniform random number generator to select genes for mutation. In this case, selection for the mutation will not depend on gene cross-diversity.  
    
**immigration_number**=*0* - Refers to the "Random Immigrants" concepts. This strategy introduces a certain number of individuals into the population during the evolution process. These new individuals are generated randomly and injected into the population.

**logging**=*False* - If this parameter has a True value, the log file will be created in the current working directory. The log file contains the flow of genetic algorithm execution, along with values of chromosomes, genes and cost functions in each generation

### Adding Variables
Variables to be optimized can be added by calling the *add* method of the *GA* object. Parameters of this method are the minimum value, the maximum value, and the step. The minimum and maximum value determine a range of possible variable values. The *step* parameter specifies the step that will be used in changing the variables values during the optimization.

For example:
```python
ga.add(1.0, 4.0, 0.01)
```
means that the corresponding parameter can have values between 1.0 and 4.0, and the step for changing variable values in optimization is 0.01.

The order in which the variables are added must match the indices of the variables in the cost function. For example, for the given function:
```python
def some_func(args):
      return math.sqrt(abs(args[0])) + math.pow(args[1], 2)
```
and instantiation of the genetic algorithm object:
```python
ga = GA(cost_function=trig_func)
```
, adding variables may look as it follows:
```python
ga.add(-25, 25, 1) # Refers to args[0]
ga.add(-5, 5, 0.1) # Refers to args[1]

```
### GA Execution and Optimisation Results
Genetic algorithm optimization executes by calling *execute* method, without parameters. This method returns the object of type *GAResults*, which contain following properties:
- **success**  - Indicates if genetic algorithm optimisation executed successfully.
- **min_cost** - The minimal cost for optimized variables
- **number_of_iterations** - The number of iterations in which the optimization reached the minimal cost
- **result_values** - The dictionary that contains variables' optimized values. The key of this dictionary is the sequence number of variable adding, and also the argument index in the cost function. The value of this dictionary is the optimized value for the variable.
- **messages** - Additional messages of the optimizations. This is a tuple structure where first value is a message level ("INFO", "WARNING" or "ERROR"), and the second value is the message text.

For example, for the given function:
```python
def some_func(args):
      return math.sqrt(abs(args[0])) + math.pow(args[1], 2)
```
, instantiation of the genetic algorithm object:
```python
ga = GA(cost_function=some_func)
```
, and variables adding:
```python
ga.add(-25, 25, 1.0) # Refers to args[0]
ga.add(-5, 5, 0.1) # Refers to args[1]

```
, the genetic algorithm execution can return results as it follows:
```python
results = ga.execute()
if results.success: # indicates if the optimisation succeeded
    print("Minimal cost: " + str(results.min_cost))
    print("Number of iterations: " + str(results.number_of_iterations))
    print("Parameter values:")
    for x in results.result_values:
        print(str(x) + ": " + str(results.result_values[x]))               
else:
    print("Calculation not successful.")

for m in results.messages:
    print(m[0] + ": " + m[1])
```
The output may look like it follows:
```
Minimal cost: 0.0
Number of iterations: 19
Parameter values:
0: 0.0
1: 0.0
```
In the case of some inadequate setting, e.g. adding not enough parameters, the output might look like it follows:
```
Calculation not succesful.
ERROR: Inadequate number of parameters for the passed function!
```
Casting results to string returns a readable strings containing all relevant data. For example:
```python
s = str(results)
print(s)
```
might return the following output:
```
Min cost: 0.0
Number of iterations: 21
Parameter values:
0: 0.0
1: 0.0
```

## GA Customisation
GAdapt follows clean architecture and SOLID principles, allowing easy customization. Create new implementations of abstract classes and pass them to the genetic algorithm through the factory object.

For example, customizing the chromosome mutation selector:

```python
import math
from gadapt.factory.ga_factory import GAFactory
from gadapt.ga import GA
from operations.mutation.population_mutation.base_chromosome_mutation_selector import BaseChromosomeMutationSelector


class BottomMutationSelector(BaseChromosomeMutationSelector):
    """
    Chromosome mutation selector which selects mutating chromosomes from the bottom of
    existing unallocated chromosomes sorted by the cost function value
    """

    def _mutate_population(self):
        if self.population is None:
            raise Exception("population must not be None")
        unallocated_chromosomes = self._get_unallocated_chromosomes(
            lambda chrom: (self.population.options.cost_function([g.variable_value for g in chrom]))
        )
        chromosomes_for_mutation = unallocated_chromosomes[
                                   len(unallocated_chromosomes) - self.number_of_mutation_chromosomes:
                                   ]
        for c in chromosomes_for_mutation:
            self._gene_mutation_selector.mutate(c, self.population.options.number_of_mutation_genes)


def some_func(args):
    return math.sqrt(abs(args[0])) + math.pow(args[1], 2)


custom_factory = GAFactory()
custom_factory.chromosome_mutation_selector = (
    BottomMutationSelector(custom_factory.chromosome_mutation_rate_determinator,
                           custom_factory.get_gene_mutation_selector()))
ga = GA(cost_function=some_func, factory=custom_factory)
ga.add(-25, 25, 1)
ga.add(-5, 5, 0.1)

print(ga.execute())
```
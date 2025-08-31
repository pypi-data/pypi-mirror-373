import math

"""
Genetic algorithm string operations
"""


def gene_value_to_string(allele):
    """
    Creates string  from the gene value
    Args:
        allele: Allele for string representation
    """
    return str(allele.gene.variable_id) + ": " + str(round(allele.variable_value, 2))


def chromosome_to_string(c):
    """
    Creates string  from the chromosome
    Args:
        c: Chromosome for string representation
    """
    str_res = "Chromosome "
    id_str = str(c.chromosome_id)
    while len(id_str) < 4:
        id_str = " " + id_str
    str_res = str_res + id_str + " - "
    for g in c:
        str_res += (
            str(g.gene.variable_id) + ": " + str(round(g.variable_value, g.gene.decimal_places)) + "; "
        )
    str_res += "Cost value: " + str(c.cost_value) + "; "
    str_res += "Chromosome generation: " + str(c.chromosome_generation) + "; "
    if not (
        c.mother_id == -1
        or c.father_id == -1
        or c.mother_id is None
        or c.father_id is None
    ):
        str_res += (
            "Mother: " + str(c.mother_id) + ", Father: " + str(c.father_id) + "; "
        )
    if c.is_mutated and len(c.mutated_variables_id_list) > 0:
        str_res += "Chromosome mutated. Mutated variables: "
        for mv in c.mutated_variables_id_list:
            str_res += str(mv) + ", "
    if c.first_mutant_generation > 0:
        str_res += "First mutant generation: " + str(c.first_mutant_generation) + "; "
    if c.last_mutant_generation > 0:
        str_res += "Last mutant generation: " + str(c.last_mutant_generation) + "; "
    if c.is_immigrant:
        str_res += "Chromosome immigrated. "
    if c.first_immigrant_generation > 0:
        str_res += (
            "First immigrant generation: " + str(c.first_immigrant_generation) + "; "
        )
    if c.last_immigrant_generation > 0:
        str_res += (
            "Last immigrant generation: " + str(c.last_immigrant_generation) + "; "
        )
    return str_res


def population_to_string_list(p):
    """
    Creates string list from the population
    Args:
        p: Population for string list representation
    """
    str_list = []
    population_for_log = [c for c in p if not math.isnan(c.cost_value)]
    population_for_log.sort(key=lambda c: c.cost_value)
    for c in population_for_log:
        str_list.append(str(c))
    return str_list


def population_to_string(p):
    """
    Creates string from the population
    Args:
        gp Population for string representation
    """
    str_res = ""
    new_line = "\n"
    str_res += "Population number: " + str(p.population_generation) + new_line
    str_res += (
        "Min Cost: "
        + str(round(p.min_cost, 2))
        + "; Avg cost: "
        + str(round(p.avg_cost, 2))
        + "; "
    )
    str_res += "Best individual variable values: " + str(p.best_individual)
    str_list = population_to_string_list(p)
    for s in str_list:
        str_res += new_line + s
    return str_res


def results_to_string(r):
    """
    Creates string from the results
    Args:
        r: Results for string representation
    """
    mess = r._get_message()
    mess_exists = not (mess is None or len(mess) == 0)
    if r.success:
        rslt = "Min cost: " + str(r.min_cost)
        rslt += "\nNumber of iterations: " + str(r.number_of_iterations)
        rslt += "\nParameter values:"
        for x in r.result_values:
            rslt += "\n" + str(x) + ": " + str(r.result_values[x])
        if mess_exists:
            rslt += "\n" + mess
    elif not mess_exists:
        rslt = "\nCalculation not succesful."
    else:
        rslt = "\n" + mess
    return rslt


def get_results_message(r):
    """
    Creates a string from the list of messages in the results
    Args:
        r: Results containing the list of messages
    """
    message = ""
    new_line = "\n"
    for m in r.messages:
        message += m[0] + ": " + m[1] + new_line
    if message.endswith(new_line):
        message = message[: -len(new_line)]
    return message

import random
from functools import reduce
from typing import List

import numpy as np

"""
Genetic algorithm utility
"""


def get_rand_bool():
    """
    Returns ranfom boolean value
    """
    rand_int = random.getrandbits(1)
    return bool(rand_int)


def get_rand_bool_with_probability(probability: float):
    """
    Returns random value with passed probability for returned value to be True
    Args:
        probability (float): The probability for True value
    """
    r = random.uniform(0, 1)
    if r <= probability:
        return True
    return False


def average(lst: List):
    """
    Average value of elements in the list
    Args:
        lst: List for finding the average value
    """
    return reduce(lambda a, b: a + b, lst) / len(lst)


def try_get_int(s):
    """
    If "s" objects is converted to int, it returns converted value.
    Othervise, returns s value.
    Args:
        s: Object to convert to int
    """
    if isinstance(s, int):
        return s
    if isinstance(s, str):
        try:
            n = int(s)
            return n
        except Exception:
            return s
    return s


def try_get_float(s):
    """
    If "s" objects is converted to float, it returns converted value.
    Othervise, returns s value.
    Args:
        s: Object to convert to float
    """
    if isinstance(s, float):
        return s
    if isinstance(s, str) or isinstance(s, int):
        try:
            n = float(s)
            return n
        except Exception:
            return s
    return s


def try_get_bool(s):
    """
    If "s" objects is converted to bool, it returns converted value.
    Othervise, returns s value.
    Args:
        s: Object to convert to bool
    """
    if isinstance(s, bool):
        return s
    if isinstance(s, str) or isinstance(s, int):
        try:
            n = bool(s)
            return n
        except Exception:
            return s
    return s


def prepare_string(s: str):
    """
    Removes spaces and new lines from the string
    Args:
        s (str): string to remove spaces and new lines
    Returns:
        str: string without spaces and new lines
    """
    str_return = s
    while " " in str_return or "\n" in str_return:
        str_return = str_return.replace(" ", "").replace("\n", "")
    return str_return


def normally_distributed_random(mean, std_dev, lower_bound, upper_bound):
    num = np.random.normal(mean, std_dev)
    num = np.clip(num, lower_bound, upper_bound)
    return num


def average_difference(diff_list):
    if len(diff_list) < 2:
        return float("NaN")
    diff_list.sort()
    differences = [diff_list[i + 1] - diff_list[i] for i in range(len(diff_list) - 1)]
    avg_difference = float(sum(differences) / len(differences))
    return avg_difference

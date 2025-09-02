from ... import SearchProblem, Node, local_expand
from ....Sampling import reservoir_sample
from typing import Callable
import itertools, math, random

def compute_probability(delta_E : float, T : float) -> float:
    probability = math.exp(delta_E/T)
    assert probability >= 0 and probability <= 1, "Probability must be between 0 and 1"

    return probability

def simulated_annealing(problem : SearchProblem, heuristic : Callable[[Node], int | float], scheduler : Callable[[int], float], stopping_temperature : float = 1e-8):
    assert 0 < stopping_temperature , "Stopping temperature must be bigger then 0"

    current_node = Node(problem.initial_state)
    current_value = heuristic(current_node)

    for i in itertools.count(start=1):
        T = scheduler(i)
        if T < stopping_temperature:
            return current_node

        random_neighbor = reservoir_sample(local_expand(problem=problem, node=current_node))
        random_neighbor_value = heuristic(random_neighbor)

        delta_E = current_value - random_neighbor_value
        if delta_E > 0 or random.random() < compute_probability(delta_E, T):
            current_node = random_neighbor
            current_value = random_neighbor_value


########## Some common schedulers ###########
def geometric_scheduler(T0 : float, alpha : float) -> Callable[[int], float]:
    assert  alpha > 0 and alpha < 1, "alpha must be between 0 and 1"
    assert T0 > 0, "T0 must be greater than 0"

    return lambda k: T0 * (alpha ** k)

def linear_scheduler(T0 : float, c : float) -> Callable[[int], float]:
    assert c > 0, "c must be greater than 0"
    assert T0 > 0, "T0 must be greater than 0"

    return lambda k: T0 - c * k

def logarith_scheduler(T0 : float) -> Callable[[int], float]:
    assert T0 > 0, "T0 must be greater than 0"

    return lambda k: T0 / math.log(1 + k)
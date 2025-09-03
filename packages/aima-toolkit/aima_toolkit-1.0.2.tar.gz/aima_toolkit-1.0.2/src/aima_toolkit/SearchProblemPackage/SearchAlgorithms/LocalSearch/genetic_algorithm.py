import typing, random, math
from typing import Any

from ...node import Node
from ...expand import expand
from ...queue import BoundedPriorityQueue
from ...searchproblem import SearchProblem, SearchStatus

def softmax(z : typing.List[typing.Union[float, int]]) -> typing.Tuple[float | typing.Any, ...]:
    exp_value: typing.List[float] = [math.exp(z_i) for z_i in z]
    sum_exp_value : float = sum(exp_value)

    return tuple(
        map(
            lambda z_i: z_i / sum_exp_value,
            exp_value
        )
    )

def mix_parents(parentA: str, parentB: str) -> tuple[str, str]:
    assert len(parentA) == len(parentB)

    random_cutoff = random.randint(1, len(parentA)-1)
    return parentA[:random_cutoff] + parentB[random_cutoff:], parentB[:random_cutoff] + parentA[random_cutoff:]

def mutate_child(child : str, mutation_rate: float, alphabet : typing.Tuple[str]) -> str:
    child_chars = list(child)
    for index, char in enumerate(child_chars):
        if random.random() < mutation_rate:
            child_chars[index] = random.choice(alphabet)

    return "".join(child_chars)

def genetic_algorithm_search(problem: SearchProblem, initial_generation : typing.List[str], population_size : int, fitness_score : typing.Callable[[str], typing.Union[float, int]], mutation_rate : float, alphabet : typing.Tuple[str]) -> typing.List[str]:
    assert population_size > 0
    assert len(initial_generation) == population_size
    assert  0 <= mutation_rate <= 1
    for state in initial_generation:
        for char in state:
            assert char in alphabet


    population = initial_generation
    best_generation = BoundedPriorityQueue(evaluation_func=lambda state: -fitness_score(state), limit=population_size)

    while True:
        solutions : typing.List[str] = list(filter(problem.IS_GOAL, population))
        if len(solutions) > 0:
            return solutions

        fitness_scores = [fitness_score(state) for state in population]
        probabilities = softmax(fitness_scores)

        choosen_parents = random.choices(population=population, weights=probabilities, k=population_size)
        for index in range(0, len(choosen_parents)-1, 2):
            parentA = choosen_parents[index]
            parentB = choosen_parents[index+1]
            childA, childB = mix_parents(parentA, parentB)

            best_generation.push(parentA)
            best_generation.push(parentB)
            best_generation.push(mutate_child(childA, mutation_rate, alphabet))
            best_generation.push(mutate_child(childB, mutation_rate, alphabet))

        # If odd pop size, carry/mutate the last parent
        if population_size % 2 == 1:
            p = choosen_parents[-1]
            best_generation.push(mutate_child(p, mutation_rate, alphabet))

        population = list(best_generation)

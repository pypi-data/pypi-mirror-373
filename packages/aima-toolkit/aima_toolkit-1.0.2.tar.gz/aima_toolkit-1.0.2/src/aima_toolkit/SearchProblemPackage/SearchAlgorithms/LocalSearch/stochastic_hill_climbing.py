from . import hill_climbing_search
from ... import SearchProblem, Heuristic, SearchStatus, local_expand, Node
from typing import Callable, Union, List, Generator, Any, Tuple
import random

def first_choice_hill_climbing_search(problem : SearchProblem, objective_function: Heuristic) -> Union[Node, SearchStatus]:
    current_node : Node = Node(problem.initial_state)
    current_value = objective_function(current_node)
    keep_going = True

    while keep_going:
        successors: List[Node] = List(
            local_expand(
                problem=problem,
                node=current_node
            )
        )
        random.shuffle(successors)

        keep_going = False
        for node in successors:
            node_value = objective_function(node)
            if node_value > current_value:
                current_node = node
                current_value = node_value
                keep_going = True
                break

    return current_node

def random_restart_hill_climbing_search(problem: SearchProblem, objective_function: Heuristic, sideway_moves_allowed : int, random_state_generator : Generator[Any, None, None]) -> Tuple[SearchStatus, Node]:
    best_node : Node = Node(problem.initial_state)
    best_value = objective_function(best_node)

    for random_state in random_state_generator:
        problem.initial_state = random_state
        node = hill_climbing_search(problem=problem, objective_function=objective_function, sideway_moves_allowed=sideway_moves_allowed)

        if problem.IS_GOAL(node.state):
            return SearchStatus.SUCCESS, node

        node_value = objective_function(node)
        if node_value > best_value:
            best_value = node_value
            best_node = node

    return SearchStatus.FAILURE, best_node
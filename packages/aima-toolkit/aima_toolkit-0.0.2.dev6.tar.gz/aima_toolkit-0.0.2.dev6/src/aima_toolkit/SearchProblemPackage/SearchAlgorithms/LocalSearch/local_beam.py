from ...node import Node
from ...expand import local_expand
from ...queue import BoundedPriorityQueue
from ...searchproblem import SearchProblem, SearchStatus, Heuristic
from ....Sampling import reservoir_sample_k
from typing import Union

def local_beam_search(problem : SearchProblem, objective_function: Heuristic, k : int) -> Union[Node, SearchStatus]:
    assert k > 0, "k must be greater than 0"

    if problem.IS_GOAL(problem.initial_state):
       return Node(problem.initial_state)

    k_rand_states = reservoir_sample_k(
        local_expand(
            problem=problem,
            node=Node(problem.initial_state)
        ),
        k=k)

    prio_queue = BoundedPriorityQueue(evaluation_func= lambda node: -objective_function(node), limit=k)
    for node in k_rand_states:
        if problem.IS_GOAL(node.state):
            return node
        else:
            prio_queue.push(node)

    while len(prio_queue) > 0:
        temp_queue = BoundedPriorityQueue(evaluation_func= lambda node: -objective_function(node), limit=k)

        for node in prio_queue:
            for successor in local_expand(problem, node):
                if problem.IS_GOAL(successor.state):
                    return successor
                else:
                    temp_queue.push(successor)

        prio_queue = temp_queue


    return SearchStatus.FAILURE



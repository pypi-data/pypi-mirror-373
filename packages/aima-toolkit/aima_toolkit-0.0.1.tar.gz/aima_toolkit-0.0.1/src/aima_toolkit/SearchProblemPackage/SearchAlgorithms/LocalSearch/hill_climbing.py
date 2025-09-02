from itertools import repeat
from typing import Callable, Any
import random
from ...node import Node
from ...expand import expand
from ...searchproblem import SearchProblem, Heuristic


def hill_climbing_search(problem : SearchProblem, objective_function : Heuristic, sideway_moves_allowed : int = 0) -> Node:
    """
    :param problem:
    :param objective_function:
    :param sideway_moves_allowed:
    :return:
    :rtype: Node
    """
    assert sideway_moves_allowed >= 0
    current_node = Node(problem.initial_state)
    current_heuristic, sidway_moves_left = objective_function(current_node), sideway_moves_allowed

    while True:
      neighbors = list(expand(problem=problem, node=current_node))
      if not neighbors:
          return current_node  # dead-end

      # evaluate once
      scored = [(objective_function(node), node) for node in neighbors]
      best_h = max(h for h, _ in scored)
      best_candidates = [node for h, node in scored if h == best_h]
      best_neighbor = random.choice(best_candidates)

      if current_heuristic < best_h:
        sidway_moves_left = sideway_moves_allowed
        current_node = best_neighbor
        current_heuristic = best_h
      elif current_heuristic == best_h and sidway_moves_left > 0:
          sidway_moves_left -= 1
          current_node = best_neighbor
      else:
        return current_node

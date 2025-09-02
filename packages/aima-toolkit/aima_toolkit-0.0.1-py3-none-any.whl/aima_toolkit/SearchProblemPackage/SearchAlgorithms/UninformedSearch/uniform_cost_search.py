from ...node import Node
from ...expand import expand
from ...queue import PriorityQueue
from ...searchproblem import SearchProblem, SearchStatus

def uniform_cost_search(problem : SearchProblem):
  node = Node(problem.initial_state)
  if problem.IS_GOAL(node.state):
    return node
  
  frontier = PriorityQueue(lambda node: node.path_cost)
  frontier.push(node)

  reached = {problem.initial_state: node}
  
  while len(frontier) > 0:
    node = frontier.pop()

    if node.path_cost > reached[node.state].path_cost:
      continue
    elif problem.IS_GOAL(node.state):
      return node

    for child in expand(problem=problem, node=node):
      if child.state not in reached.keys() or child.path_cost < reached[child.state].path_cost:
        reached[child.state] = child
        frontier.push(child)

  return SearchStatus.FAILURE
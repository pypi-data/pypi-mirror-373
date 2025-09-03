from ...node import Node
from ...expand import expand
from ...queue import Stack
from ...searchproblem import SearchProblem, SearchStatus

def depth_first_search(problem : SearchProblem):
  node = Node(problem.initial_state)
  if problem.IS_GOAL(node.state):
    return node

  frontier = Stack()
  frontier.push(node)

  while len(frontier) > 0:
    node = frontier.pop()

    for child in expand(problem=problem, node=node):
      if problem.IS_GOAL(child.state):
        return child
      else:
        frontier.push(child)

  return SearchStatus.FAILURE
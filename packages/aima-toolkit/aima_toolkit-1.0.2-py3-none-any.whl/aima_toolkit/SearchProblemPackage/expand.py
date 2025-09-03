from .node import Node
from .searchproblem import SearchProblem

def expand(problem : SearchProblem, node : Node):
  state = node.state

  for action in problem.ACTIONS(state):
    new_state = problem.RESULTS(state=state, action=action)

    cost = node.path_cost + problem.ACTION_COST(state = state, action = action, new_state = new_state)

    yield Node(new_state, parent=node, path_cost= cost, action=action)

def local_expand(problem: SearchProblem, node : Node):
    """
    Takes a node and expands it locally, not saving the path and only showing nodes that are local
    :param problem:
    :param node:
    :return:
    """
    state = node.state

    for action in problem.ACTIONS(state):
        new_state = problem.RESULTS(state=state, action=action)

        yield Node(new_state)
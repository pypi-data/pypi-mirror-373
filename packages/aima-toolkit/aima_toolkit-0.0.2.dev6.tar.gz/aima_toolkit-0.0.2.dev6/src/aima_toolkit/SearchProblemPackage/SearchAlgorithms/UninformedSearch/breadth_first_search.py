from ...node import Node
from ...expand import expand
from ...queue import FIFOQueue
from ...searchproblem import SearchProblem, SearchStatus

def breadth_first_search(problem: SearchProblem):
    node = Node(problem.initial_state)
    if problem.IS_GOAL(node.state):
        return node

    frontier = FIFOQueue()
    frontier.push(node)

    reached = [problem.initial_state]

    while len(frontier) > 0:
        node = frontier.pop()

        for child in expand(problem=problem, node=node):
            if problem.IS_GOAL(child.state):
                return child
            elif child.state not in reached:
                reached.append(child.state)
                frontier.push(child)

    return SearchStatus.FAILURE

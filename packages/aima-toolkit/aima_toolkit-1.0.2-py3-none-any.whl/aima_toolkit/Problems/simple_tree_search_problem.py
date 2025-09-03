from ..SearchProblemPackage.searchproblem import SearchProblem
class Tree_Search_Problem(SearchProblem):
    tree = {
       'A' : ['B', 'C'],
       'B' : ['D', 'E'],
       'D' : [],
       'E' : [],
       'C' : ['F', 'G'],
       'F' : [],
       'G' : []
    }

    def __init__(self, initial_state, goal_state):
        super().__init__(initial_state)
        self.goal_state = goal_state

    def ACTIONS(self, states):
        return Tree_Search_Problem.tree[states].copy()

    def RESULTS(self, state, action):
        if action not in Tree_Search_Problem.tree[state]:
            raise ValueError(f"Action {action} is not valid for state {state}.")

        return action

    def ACTION_COST(self, state, action, new_state):
        return 1

    def IS_GOAL(self, state):
        return state == self.goal_state

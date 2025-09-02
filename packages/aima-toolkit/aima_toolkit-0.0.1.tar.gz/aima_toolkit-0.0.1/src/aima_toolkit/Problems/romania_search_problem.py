from ..SearchProblemPackage.searchproblem import SearchProblem

class Romania_Search_Problem(SearchProblem):
    romania_graph_map = {
        'Arad': {'Zerind': 75, 'Sibiu': 140, 'Timisoara': 118},
        'Zerind': {'Arad': 75, 'Oradea': 71},
        'Oradea': {'Zerind': 71, 'Sibiu': 151},
        'Sibiu': {'Arad': 140, 'Oradea': 151, 'Fagaras': 99, 'Rimnicu Vilcea': 80},
        'Timisoara': {'Arad': 118, 'Lugoj': 111},
        'Lugoj': {'Timisoara': 111, 'Mehadia': 70},
        'Mehadia': {'Lugoj': 70, 'Drobeta': 75},
        'Drobeta': {'Mehadia': 75, 'Craiova': 120},
        'Craiova': {'Drobeta': 120, 'Rimnicu Vilcea': 146, 'Pitesti': 138},
        'Rimnicu Vilcea': {'Sibiu': 80, 'Craiova': 146, 'Pitesti': 97},
        'Fagaras': {'Sibiu': 99, 'Bucharest': 211},
        'Pitesti': {'Craiova': 138, 'Rimnicu Vilcea': 97, 'Bucharest': 101},
        'Bucharest': {'Fagaras': 211, 'Pitesti': 101, 'Giurgiu': 90},
        'Giurgiu': {'Bucharest': 90}
    }

    def __init__(self, initial_state, goal_state):
        super().__init__(initial_state)
        self.goal_state = goal_state

    def ACTIONS(self, states):
        return Romania_Search_Problem.romania_graph_map[states].keys()

    def RESULTS(self, state, action):
        if Romania_Search_Problem.romania_graph_map[state].get(action) is None:
            raise ValueError(f"Action {action} is not valid for state {state}.")

        return action

    def ACTION_COST(self, state, action, new_state):
        return Romania_Search_Problem.romania_graph_map[state][action]

    def IS_GOAL(self, state):
        return state == self.goal_state

class Romania_Search_Problem_Uniform_Cost(SearchProblem):
    romania_graph_map = {
        'Arad': ['Zerind', 'Sibiu', 'Timisoara'],
        'Zerind': ['Arad', 'Oradea'],
        'Oradea': ['Zerind', 'Sibiu'],
        'Sibiu': ['Arad', 'Oradea', 'Fagaras', 'Rimnicu Vilcea'],
        'Timisoara': ['Arad', 'Lugoj'],
        'Lugoj': ['Timisoara', 'Mehadia'],
        'Mehadia': ['Lugoj', 'Drobeta'],
        'Drobeta': ['Mehadia', 'Craiova'],
        'Craiova': ['Drobeta', 'Rimnicu Vilcea', 'Pitesti'],
        'Rimnicu Vilcea': ['Sibiu', 'Craiova', 'Pitesti'],
        'Fagaras': ['Sibiu', 'Bucharest'],
        'Pitesti': ['Craiova', 'Rimnicu Vilcea', 'Bucharest'],
        'Bucharest': ['Fagaras', 'Pitesti', 'Giurgiu'],
        'Giurgiu': ['Bucharest']
    }

    def __init__(self, initial_state, goal_state):
        super().__init__(initial_state)
        self.goal_state = goal_state

    def ACTIONS(self, states):
        return Romania_Search_Problem_Uniform_Cost.romania_graph_map[states].copy()

    def RESULTS(self, state, action):
        if action not in Romania_Search_Problem_Uniform_Cost.romania_graph_map[state]:
            raise ValueError(f"Action {action} is not valid for state {state}.")

        return action

    def ACTION_COST(self, state, action, new_state):
        return 1

    def IS_GOAL(self, state):
        return state == self.goal_state

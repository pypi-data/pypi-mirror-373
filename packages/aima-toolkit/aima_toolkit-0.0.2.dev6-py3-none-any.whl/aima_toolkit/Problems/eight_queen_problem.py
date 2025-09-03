from ..SearchProblemPackage import Node, SearchProblem, SearchStatus
import random

class EightQueenProblem(SearchProblem):
  def __init__(self, initial_state : str):
    assert len(initial_state) == 8
    assert set(initial_state).issubset(set('12345678'))

    super().__init__(initial_state)

  def ACTIONS(self, states):
    all_states = set("12345678")
    actions = []

    for index, queen_position in enumerate(states):
      for legal_state in all_states.difference(set(queen_position)):
        actions.append(f"{index}_{legal_state}")

    return actions


  def ACTION_COST(self, state, action, new_state):
    return 1
  
  def RESULTS(self, state, action : str):
    queen_index, new_pos = EightQueenProblem._action_to_data(action=action)
    new_state = list(state)
    new_state[queen_index] = new_pos

    return "".join(new_state)
  
  def IS_GOAL(self, state : str):
    return EightQueenProblem.heuristic(Node(state)) == 0
  
  @staticmethod
  def _action_to_data(action : str) -> tuple[int, str]:
    action_values = action.split('_')
    return int(action_values[0]), action_values[1]

  @staticmethod
  def heuristic(node : Node) -> int:
    state = node.state

    queen_position = [int(pos) for pos in list(state)]
    h = 0

    for i in range(len(queen_position)):
      for j in range(i + 1, len(queen_position)):
        distance = j - i
        queen_distance = abs(queen_position[j] - queen_position[i])
        if queen_distance == 0 or queen_distance == distance:
          h += 1

    return h

  @staticmethod
  def random_initial_state() -> str:
    return "".join(random.choices("12345678", k=8))


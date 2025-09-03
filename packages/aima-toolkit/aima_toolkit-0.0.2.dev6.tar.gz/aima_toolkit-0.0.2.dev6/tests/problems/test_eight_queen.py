from src.aima_toolkit.SearchProblemPackage import Node
from src.aima_toolkit.Problems import EightQueenProblem

def test_action():
  test_state = "11111111"
  problem = EightQueenProblem(test_state)

  # which queen, new pos
  for queen in range(8):
    for new_pos in "2345678":
      action = f"{queen}_{new_pos}"
      expected = list(test_state)
      expected[queen] = new_pos
      expected = "".join(expected)

      assert problem.RESULTS(test_state, action) == expected

def test_heuristic():
  test_state = "11111111"

  assert EightQueenProblem.heuristic(Node("11111111")) == 7+6+5+4+3+2+1
  assert EightQueenProblem.heuristic(Node("83742516")) == 1

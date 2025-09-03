from src.aima_toolkit.Problems import Romania_Search_Problem, Romania_Search_Problem_Uniform_Cost
from src.aima_toolkit.SearchProblemPackage.SearchAlgorithms.UninformedSearch import uniform_cost_search
from src.aima_toolkit.SearchProblemPackage import SearchStatus

class TestSmallestCost():
  def test_arad_to_giurgiu(self):
    result_node = uniform_cost_search(Romania_Search_Problem(initial_state="Arad", goal_state="Giurgiu"))
    list_of_states = result_node.get_path() if result_node else []
    assert list_of_states == ["Arad", "Sibiu", "Rimnicu Vilcea", "Pitesti", "Bucharest", "Giurgiu"]

  def test_sibiu_to_bucharest(self):
    result_node = uniform_cost_search(Romania_Search_Problem(initial_state="Sibiu", goal_state="Bucharest"))
    list_of_states = result_node.get_path() if result_node else []
    assert list_of_states == ["Sibiu", "Rimnicu Vilcea", "Pitesti", "Bucharest"]

class TestSameCost():
  def test_arad_to_giurgiu(self):
    result_node = uniform_cost_search(Romania_Search_Problem_Uniform_Cost(initial_state="Arad", goal_state="Giurgiu"))
    list_of_states = result_node.get_path() if result_node else []
    assert list_of_states == ["Arad", "Sibiu", "Fagaras", "Bucharest","Giurgiu"]

  def test_arad_to_arad(self):
    result_node = uniform_cost_search(Romania_Search_Problem_Uniform_Cost(initial_state="Arad", goal_state="Arad"))
    list_of_states = result_node.get_path() if result_node else []
    assert list_of_states == ["Arad"]

  def test_arad_to_nothing(self):
    result_node = uniform_cost_search(Romania_Search_Problem_Uniform_Cost(initial_state="Arad", goal_state="Nothing"))
    assert result_node == SearchStatus.FAILURE
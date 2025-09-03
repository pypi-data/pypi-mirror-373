from src.aima_toolkit.Problems import Tree_Search_Problem
from src.aima_toolkit.SearchProblemPackage import SearchStatus
from src.aima_toolkit.SearchProblemPackage.SearchAlgorithms.UninformedSearch import depth_limited_search, iterative_deepening_search

class TestDepthLimitedSearch:
    def test_A_to_G_depth_bad(self):
        problem = Tree_Search_Problem(initial_state='A', goal_state='G')
        result_node = depth_limited_search(problem, limit=1)

        assert result_node == SearchStatus.CUTOFF

    def test_A_to_H_depth_good(self):
        problem = Tree_Search_Problem(initial_state='A', goal_state='H')
        result_node = depth_limited_search(problem, limit=10)

        assert result_node == SearchStatus.FAILURE

    def test_A_to_G_depth_good(self):
        problem = Tree_Search_Problem(initial_state='A', goal_state='G')
        result_node = depth_limited_search(problem, limit=10)

        assert result_node != SearchStatus.FAILURE
        assert result_node.get_path() == ['A', 'C', 'G']

    def test_A_to_A_depth_good(self):
        problem = Tree_Search_Problem(initial_state='A', goal_state='A')
        result_node = depth_limited_search(problem, limit=0)

        assert result_node != SearchStatus.FAILURE
        assert result_node.get_path() == ['A']

class TestIterativeDeepeningSearch:
    def test_A_to_A(self):
        problem = Tree_Search_Problem(initial_state='A', goal_state='A')
        result_node = iterative_deepening_search(problem)

        assert result_node != SearchStatus.FAILURE
        assert result_node.get_path() == ['A']

    def test_A_to_B(self):
        problem = Tree_Search_Problem(initial_state='A', goal_state='B')
        result_node = iterative_deepening_search(problem)

        assert result_node != SearchStatus.FAILURE
        assert result_node.get_path() == ['A', 'B']

    def test_A_to_C(self):
        problem = Tree_Search_Problem(initial_state='A', goal_state='C')
        result_node = iterative_deepening_search(problem)

        assert result_node != SearchStatus.FAILURE
        assert result_node.get_path() == ['A', 'C']

    def test_A_to_D(self):
        problem = Tree_Search_Problem(initial_state='A', goal_state='D')
        result_node = iterative_deepening_search(problem)

        assert result_node != SearchStatus.FAILURE
        assert result_node.get_path() == ['A', 'B', 'D']

    def test_A_to_E(self):
        problem = Tree_Search_Problem(initial_state='A', goal_state='E')
        result_node = iterative_deepening_search(problem)

        assert result_node != SearchStatus.FAILURE
        assert result_node.get_path() == ['A', 'B', 'E']
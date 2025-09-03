from itertools import count
from .depth_limited_search import depth_limited_search
from ...searchproblem import SearchProblem, SearchStatus

def iterative_deepening_search(problem : SearchProblem):
  for depth in count(start=0):
    result = depth_limited_search(problem, depth)
    if result != SearchStatus.CUTOFF:
      return result
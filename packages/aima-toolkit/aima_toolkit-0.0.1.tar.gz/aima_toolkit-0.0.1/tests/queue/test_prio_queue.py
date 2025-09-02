from src.aima_toolkit.SearchProblemPackage import PriorityQueue, BoundedPriorityQueue

def test_prio_que():
  pri_que = PriorityQueue(lambda x: x)

  pri_que.push(3)
  pri_que.push(6)
  pri_que.push(0)
  pri_que.push(-4)
  pri_que.push(-4)

  assert pri_que.best() == [-4, -4]
  assert pri_que.pop() == -4
  assert pri_que.best() == [-4]
  assert pri_que.pop() == -4
  assert pri_que.pop() == 0
  assert pri_que.pop() == 3
  assert pri_que.pop() == 6
  assert pri_que.best() == []
  
def test_bounded_prio_que():
  pri_que = BoundedPriorityQueue(evaluation_func=lambda x: x, limit=3)
  pri_que.push(3)
  pri_que.push(6)
  pri_que.push(0)
  pri_que.push(-4)
  pri_que.push(9)

  assert len(pri_que) == 3
  assert pri_que.pop() == -4
  assert pri_que.pop() == 0
  assert pri_que.pop() == 3
  assert len(pri_que) == 0

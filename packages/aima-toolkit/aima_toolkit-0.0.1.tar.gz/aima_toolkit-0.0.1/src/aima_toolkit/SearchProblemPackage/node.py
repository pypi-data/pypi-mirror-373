class Node():
  def __init__(self, state, parent = None, path_cost = 0, action = None):
    self.state = state
    self.parent = parent
    self.path_cost = path_cost
    self.depth = 0 if parent is None else parent.depth + 1
    self.action = action

  def __str__(self):
    return self.__repr__()

  def __eq__(self, value: object) -> bool:
    return self.state == value.state if isinstance(value, Node) else False

  def __repr__(self):
    return f"Node({self.state}, cost={self.path_cost})"

  def get_path(self):
    path = []
    current = self
    while current:
      path.append(current.state)
      current = current.parent

    return path[::-1]
  
  def get_actions(self):
    actions = []
    current = self
    while current:
      if current.action is not None:
        actions.append(current.action)
      current = current.parent

    return actions[::-1]
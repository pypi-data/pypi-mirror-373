from abc import ABC

class Factory(ABC):

  def create(self, mode: str):
    method_name = f"create_{mode.lower()}"
    if not hasattr(self, method_name):
      return None
    method = getattr(self, method_name)
    return method()

  
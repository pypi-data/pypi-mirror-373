from functools import wraps
from .WaiterDeco import WaiterDeco

class ECTextDeco(WaiterDeco):

  def __call__(self,func):
    @wraps(func) 
    def wrapper(*args,**kwargs):
      return self.wrapper(func,*args,**kwargs)
    return wrapper

  def set_arg_index(self):
    self.arg_value_index = 1

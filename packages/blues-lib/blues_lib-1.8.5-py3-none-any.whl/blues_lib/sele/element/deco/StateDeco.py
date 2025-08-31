from functools import wraps
from .InfoDeco import InfoDeco

class StateDeco(InfoDeco):

  caller_class = 'State'

  def __call__(self,func):
    @wraps(func) 
    def wrapper(*args,**kwargs):
      return self.wrapper(func,*args,**kwargs)
    return wrapper


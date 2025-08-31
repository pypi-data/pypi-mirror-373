from functools import wraps
from .InfoDeco import InfoDeco

class SelectDeco(InfoDeco):

  caller_class = 'Select'

  def __call__(self,func):
    @wraps(func) 
    def wrapper(*args,**kwargs):
      return self.wrapper(func,*args,**kwargs)
    return wrapper


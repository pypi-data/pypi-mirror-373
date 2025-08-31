from functools import wraps
from .InfoDeco import InfoDeco

class SelectKeyDeco(InfoDeco):

  caller_class = 'Select'

  def __call__(self,func):
    @wraps(func) 
    def wrapper(*args,**kwargs):
      return self.wrapper(func,*args,**kwargs)
    return wrapper

  def set_arg_index(self):
    self.arg_key_index = 1
    self.arg_cs_index = 2
    self.arg_pcs_index = 3


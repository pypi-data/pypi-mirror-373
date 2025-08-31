from functools import wraps
from .InfoDeco import InfoDeco

class InfoKeyDeco(InfoDeco):

  def __call__(self,func):
    @wraps(func) 
    def wrapper(*args,**kwargs):
      return self.wrapper(func,*args,**kwargs)
    return wrapper

  def set_arg_index(self):
    self.arg_cs_index = 1
    self.arg_key_index = 2
    self.arg_pcs_index = 3


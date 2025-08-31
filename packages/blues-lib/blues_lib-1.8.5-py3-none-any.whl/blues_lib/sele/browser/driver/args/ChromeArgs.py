from abc import ABC,abstractmethod

class ChromeArgs(ABC):

  def __init__(self,args=None):
    '''
    @param {dict} args : the input experimental args dict, such as {'debugaddr':'127.0.0.1:9222'}
      - the dict's key is not the real option attr
    ''' 
    self._input_args = args 

  @abstractmethod 
  def get():
    pass

  @abstractmethod 
  def get_from_input():
    pass

import sys,os,re
from abc import ABC,abstractmethod
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))

class CleanerHandler(ABC):

  def __init__(self):
    '''
    The abstract class of handlers 
    '''
    self._next_handler = None
    self.message = ''
  
  def set_next(self,handler):
    '''
    Set the next handler
    Parameter:
      handler {Handler} : the next handler
    Returns 
      {Handler} 
    '''
    self._next_handler = handler
    return handler

  def handle(self,request):
    '''
    The full cleanup handlers chain
    Args:
      request {dict} : 
        - db {dict}
        - file {dict}
    Returns 
      {dict} : this last handler's handled response
    '''
    response =self.resolve(request)
    # It's a pipeline, don't stop, go throght all handlers
    if self._next_handler:
      return self._next_handler.handle(request)
    else:
      return response

  @abstractmethod
  def resolve(self,data):
    '''
    This method will be implemented by subclasses
    '''
    pass

  def set_message(self,response):
    self.message = response['message']


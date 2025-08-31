import abc
class HttpMessageFilter(metaclass=abc.ABCMeta):
  
  def __init__(self):
    self.__next = None

  def set_next(self,next):
    self.__next = next
    return next

  @abc.abstractmethod
  def resolve(self,messages):
    '''
    @description : the concrete filter method
    '''
    pass

  def filter(self,messages):
    '''
    @description : the final method, invoke the next filter automatically
    '''
    reqs = self.resolve(messages)
    if self.__next:
      # prev return value as the next filter's input
      return self.__next.filter(reqs)
    else:
      return reqs

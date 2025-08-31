from .Querier import Querier 
from .EC import EC 
from .Expecter import Expecter 

class Waiter():

  def __init__(self,driver):
    self.querier = Querier(driver)
    self.ec = EC(driver)
    self.expecter = Expecter(driver)

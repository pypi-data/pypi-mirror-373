from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions 
from selenium.common.exceptions import NoSuchElementException 
from selenium.common.exceptions import ElementNotInteractableException 
from .deco.ExpecterDeco import ExpecterDeco

class Expecter():
  '''
  Define custom expected conditions
  '''

  def __init__(self,driver):
    self.__driver = driver
    self.__timeout = 10
    self.__poll_frequency = 0.5
    self.__ignored_exceptions = [NoSuchElementException,ElementNotInteractableException]
    self.__timeout_message = 'timeout'

  #-- module 9: wait by self-defined func --#
  @ExpecterDeco('until')
  def until(self,func,timeout=5,poll_frequency=None,ignored_exceptions=None,timeout_message=None):
    # this func has a para is the driver
    wait_timeout = timeout if timeout else self.__timeout
    wait_poll_frequency = poll_frequency if poll_frequency else self.__poll_frequency
    wait_ignored_exceptions = ignored_exceptions if ignored_exceptions else self.__ignored_exceptions
    wait_timeout_message = timeout_message if timeout_message else self.__timeout_message
    
    # can return any type result
    return WebDriverWait(self.__driver,wait_timeout,wait_poll_frequency,wait_ignored_exceptions).until(func,wait_timeout_message)

  def __demo_func(driver):
    '''
    The first parameter (driver) must be accepted
    This func's return value will be the until's return value
    '''
    return driver.current_url

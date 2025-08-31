import sys,os,re
from selenium.webdriver.remote.webelement import WebElement
from .EC import EC   
from .deco.QuerierDeco import QuerierDeco

sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from sele.element.Finder import Finder   

# 提供元素选择功能
class Querier():

  def __init__(self,driver,timeout=8):
    self.__driver = driver
    self.__ec = EC(driver) 
    self.__finder = Finder(driver) 
    self.__timeout = timeout or 5

  def setTimeout(self,timeout=5):
    '''
    Adjust the timeout in runtime
    '''
    self.__timeout = timeout

  @QuerierDeco('query')
  def query(self,target_CS_WE,parent_CS_WE=None,timeout=5):
    '''
    Wait and get the element from document or parent element
    Parameter:
      target_CS_WE {str|WebElement} : the target element's css selector or WebElement
      parent_CS_WE {str|WebElement} : the parent element's css selector or WebElement
      timeout {int} : Maximum waiting time (s)
    Returns:
      {WebElement} 
    '''

    if not parent_CS_WE:
      # Scenaria 1: without the parent
      return self.__query(target_CS_WE,timeout)
    else:
      # Scenaria 2: with a the parent, wait the parent and find
      parent_element = self.__query(parent_CS_WE,timeout)
      return self.__finder.find(target_CS_WE,parent_CS_WE)

  @QuerierDeco('query_all')
  def query_all(self,target_CS_WE,parent_CS_WE=None,timeout=5):
    '''
    Wait and get elements from document or parent element
    Parameter:
      target_CS_WE {str|WebElement} : the target element's css selector or WebElement
      parent_CS_WE {str|WebElement} : the parent element's css selector or WebElement
      timeout {int} : Maximum waiting time (s)
    Returns:
      {list<WebElement>} 
    '''
    if not parent_CS_WE:
      # Scenaria 1: without the parent
      return self.__query_all(target_CS_WE,timeout)
    else:
      # Scenaria 2: with a the parent, wait the parent and find
      parent_element = self.__query(parent_CS_WE,timeout)
      return self.__finder.find_all(target_CS_WE,parent_CS_WE)

  def __query(self,target_CS_WE,timeout=5,parent_WE=None):
    '''
    Wait and Get the target WebElement
    Parameter:
      target_CS_WE {str|WebElement} : the target element's css selector or WebElement
      timeout {int} : Maximum waiting time (s)
    Returns:
      {WebElement} 
    '''
    if type(target_CS_WE) == WebElement:
      return target_CS_WE
    
    wait_time = timeout if timeout else self.__timeout
    return self.__ec.to_be_presence(target_CS_WE,wait_time,parent_WE)

  def __query_all(self,target_CS_WE,timeout=5):
    '''
    Wait and Get the target WebElements
    Parameter:
      target_CS_WE {str|WebElement} : css selector or web element
      timeout {int} : Maximum waiting time (s)
    Returns:
      {list<WebElement>} 
    '''
    if type(target_CS_WE) == WebElement:
      return [target_CS_WE]

    wait_time = timeout if timeout else self.__timeout
    return self.__ec.all_to_be_presence(target_CS_WE,wait_time)

   

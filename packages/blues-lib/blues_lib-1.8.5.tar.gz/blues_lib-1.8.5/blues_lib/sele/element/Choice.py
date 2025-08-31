import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from sele.waiter.Querier import Querier 
from sele.action.Mouse import Mouse 

class Choice():
  
  def __init__(self,driver):
    self.__driver = driver
    self.__querier = Querier(driver,5)
    self.__mouse = Mouse(driver)

  def select(self,target_CS_WE,parent_CS_WE=None,timeout=5):
    '''
    Support multi input parameters as selectors
    Parameter:
      target_CS_WE {str|WebElemnt|list<str>|list<WebElement>} : one or a list of target element
      parent_CS_WE {str|WebElemnt} : the choicebox's parent element
    Returns:
      {int} : the selectd count
    '''
    count = 0
    if not target_CS_WE:
      return count

    target_CS_WEs = target_CS_WE if type(target_CS_WE) == list else [target_CS_WE]
    for target_CS_WE in target_CS_WEs:
      count += self.__toggle(target_CS_WE,True,parent_CS_WE,timeout)
    return count

  def deselect(self,target_CS_WE,parent_CS_WE=None,timeout=5):
    '''
    Support multi input parameters as selectors
    Parameter:
      target_CS_WE {str|WebElemnt|list<str>|list<WebElement>} : one or a list of target element
    Returns:
      {int} : the selectd count
    '''
    count = 0
    if not target_CS_WE:
      return count
    
    target_CS_WEs = target_CS_WE if type(target_CS_WE) == list else [target_CS_WE]

    for target_CS_WE in target_CS_WEs:
      count += self.__toggle(target_CS_WE,False,parent_CS_WE,timeout)
    return count

  def __toggle(self,target_CS_WE,checked=True,parent_CS_WE=None,timeout=5):
    '''
    Select the choice boxes by selectors
    Parameter
      target_CS_WE {str|WebElement} : boxes css selectors or WebElement
      - Maybe one element: 'iput[value=car]'
      - Maybe multi elements: 'input[value=car],input[value=boat]'
    Returns:
      {int} : selectd count
    '''
    count = 0
    web_elements = self.__querier.query_all(target_CS_WE,parent_CS_WE,timeout)
    if not web_elements:
      return count
    
    for web_element in web_elements:
      # select mode
      if checked and web_element.is_selected():
        continue
      # deselect mode
      if not checked and not web_element.is_selected():
        continue
      count+=1
      # use the action to roll in the element to viewport automatically
      self.__mouse.click(web_element)
    return count

  def is_selected(self,target_CS_WE,parent_CS_WE=None,timeout=5):
    web_element = self.__querier.query(target_CS_WE,parent_CS_WE,timeout)
    if not web_element:
      return False
    return web_element.is_selected()

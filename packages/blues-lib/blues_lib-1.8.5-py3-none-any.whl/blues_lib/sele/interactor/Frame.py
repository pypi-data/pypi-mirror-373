import sys,os,re
from .deco.SwitchDeco import SwitchDeco
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from sele.waiter.Querier import Querier

class Frame():
 
  def __init__(self,driver):
    self.__driver = driver
    self.__querier = Querier(driver)
  
  @SwitchDeco('Frame','switch_to',1)
  def switch_to(self,target_CS_WE):
    '''
    Switch the driver's focus to the specific frame
    Parameter:
      target_CS_WE {str|WebElement} : the frame's css selector or webelement
    Returns:
      {None}
    '''
    web_element = self.__querier.query(target_CS_WE)
    if not web_element:
      return False
    try:
      self.__driver.switch_to.frame(web_element)
      return True
    except:
      return False
      
  @SwitchDeco('Frame','switch_to_default')
  def switch_to_default(self):
    '''
    Switch to the default window that the driver opened
    Returns:
      {None}
    '''
    try:
      self.__driver.switch_to.default_content()
      return True
    except:
      return False

  @SwitchDeco('Frame','switch_to_parent')
  def switch_to_parent(self):
    '''
    Switch to the current frame's parent window, mybe not the default window
    Returns:
      {None}
    '''
    try:
      self.__driver.switch_to.parent_frame()
      return True
    except:
      return False

  @SwitchDeco('Frame','execute',1)
  def execute(self,target_CS_WE,func):
    '''
    Switch to a frame, execute a function and back to the default window
    Parameter:
      target_CS_WE {str|WebElement} : the frame's css selector or webelement
      func {function} : ececute in the iframe window
    Returns:
      {any} : the func's return value
    '''
    self.switch_to(target_CS_WE)
    value = func()
    self.switch_to_default()
    return value
      

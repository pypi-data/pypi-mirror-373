import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from sele.waiter.Querier import Querier  
from selenium.webdriver import ActionChains
from selenium.webdriver.common.actions.action_builder import ActionBuilder

class Mouse():
  '''
  If the element is outside the viewable window, 
  The element will automatically roll into the window, 
  With the bottom of the element flush with the bottom of the window
  '''
  def __init__(self,driver):
    self.__driver = driver
    self.__querier = Querier(driver)
    self.__chains = ActionChains(driver)
    self.__builder = ActionBuilder(driver)

  # == module 1 : click event == #
  # add a  hover deco
  # other method: hover().pause(1).click().perform()
  def click(self,target_CS_WE,parent_CS_WE=None,timeout=5):
    '''
    Click and release
    Parameter:
      target_CS_WE {str | WebElement}
    '''
    web_element = self.__querier.query(target_CS_WE,parent_CS_WE,timeout)
    if not web_element:
      return

    self.__chains.click(web_element).perform()
  
  def right_click(self,target_CS_WE,parent_CS_WE=None,timeout=5):
    '''
    Right click and release
    Parameter:
      target_CS_WE {str | WebElement}
    '''
    web_element = self.__querier.query(target_CS_WE,parent_CS_WE,timeout)
    if not web_element:
      return
    self.__chains.context_click(web_element).perform()

  def double_click(self,target_CS_WE,parent_CS_WE=None,timeout=5):
    '''
    Double left click
    Parameter:
      target_CS_WE {str | WebElement}
    '''
    web_element = self.__querier.query(target_CS_WE,parent_CS_WE,timeout)
    if not web_element:
      return
    self.__chains.double_click(web_element).perform()

  # == module 2 : hold and release == #
  def hold(self,target_CS_WE,parent_CS_WE=None,timeout=5):
    '''
    Click and hold
    Parameter:
      target_CS_WE {str | WebElement}
    '''
    web_element = self.__querier.query(target_CS_WE,parent_CS_WE,timeout)
    if not web_element:
      return
    self.__chains.click_and_hold(web_element).perform()

  def release(self,target_CS_WE,parent_CS_WE=None,timeout=5):
    '''
    Release the hold
    Parameter:
      target_CS_WE {str | WebElement}
    '''
    web_element = self.__querier.query(target_CS_WE,parent_CS_WE,timeout)
    self.__chains.release(web_element).perform()

  # == module 3 : move into a element == #
  def move_in(self,target_CS_WE,parent_CS_WE=None,timeout=5):
    '''
    Moves the mouse to the in-view center point of the element
    If the element outside in the viewport, it will move into the viewport automatically
    Automaic moving : the element's bottom border align to the window's bottom border
    Parameter:
      target_CS_WE {str | WebElement}
    '''
    web_element = self.__querier.query(target_CS_WE,parent_CS_WE,timeout)
    if not web_element:
      return
    self.__chains.move_to_element(web_element).perform()

  def move_in_offset(self,target_CS_WE,offset_x=0,offset_y=0,parent_CS_WE=None,timeout=5):
    '''
    Offset form the element
    This method moves the mouse to the in-view center point of the element, 
    Then moves by the provided offset.
    '''
    web_element = self.__querier.query(target_CS_WE,parent_CS_WE,timeout)
    if not web_element:
      return
    self.__chains.move_to_element_with_offset(web_element,offset_x,offset_y).perform()

  # == module 4 : move by the viewport == #
  def move_to(self,x=0,y=0):
    '''
    Offset from Viewport
    The viewport's top left point to the element's center point (not the element's top left point)
    Test with hold
    '''
    self.__builder.pointer_action.move_to_location(x,y)
    self.__builder.perform()

  def move_to_offset(self,offset_x=0,offset_y=0):
    '''
    Offset from Viewport
    This method moves the mouse from its current position by the offset provided by the user. 
    Test with hold
    '''
    self.__chains.move_by_offset(offset_x,offset_y).perform()


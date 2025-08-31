import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from sele.element.Finder import Finder 
from sele.element.State import State 
from sele.interactor.Frame import Frame 
from sele.script.javascript.JavaScript import JavaScript 

class Popup():
  '''
  Handle automatic pop-up AD boxes
  '''
  def __init__(self,driver):
    self.__driver = driver
    self.__finder = Finder(driver)
    self.__state = State(driver)
    self.__frame = Frame(driver)
    self.__javascript = JavaScript(driver)

  def remove(self,target_CS_WE):
    '''
    Remove the popup elements
    Parameter:
      target_CS_WE {list<str>} : target_CSs selector list
    Returns:
      {int} : removed count
    '''
    count = 0
    if not target_CS_WE:
      return count
    
    target_CS_WEs = target_CS_WE if type(target_CS_WE) == list else [target_CS_WE]

    for CS_WE in target_CS_WEs:
      count += self.__javascript.remove(CS_WE)

    return count

  def close(self,target_CS_WE,parent_CS_WE=None,frame_CS_WE=None):
    '''
    Close one or multi popups
    Parameter:
      off_locators { list<[close_CS_WE,frame_CS_WE]> | list<close_CS_WE>} 
    Returns:
      {int} : the closed count
    '''
    count = 0
    if not target_CS_WE:
      return count

    target_CS_WEs = target_CS_WE if type(target_CS_WE)==list else [target_CS_WE]
    
    for CS_WE in target_CS_WEs:
      count += self.__close(CS_WE,parent_CS_WE,frame_CS_WE)

    return count

  def __close(self,close_CS_WE,parent_CS_WE=None,frame_CS_WE=None):
    count = 0
    # switch to frame
    if frame_CS_WE:
      self.__frame.switch_to(frame_CS_WE)      

    web_elements = self.__finder.find_all(close_CS_WE,parent_CS_WE)
    if not web_elements:
      # switch back
      if frame_CS_WE:
        self.__frame.switch_to_default()      

      return count
    
    for web_element in web_elements:
      if self.__state.is_displayed(web_element):
        count+=1
        self.__mouse.click(web_element)
    
    # switch back
    if frame_CS_WE:
      self.__frame.switch_to_default()      

    return count



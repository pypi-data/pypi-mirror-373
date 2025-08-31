import sys,os,re
from .Finder import Finder   
from .deco.StateDeco import StateDeco

# 提供元素选择功能
class State():

  def __init__(self,driver):
    self.__driver = driver
    self.__finder = Finder(driver)

  # === part 4: get element's state, don't wiat === #
  @StateDeco('is_presence')
  def is_presence(self,target_CS_WE,parent_CS_WE=None):
    '''
    Detemines if the element is in the document
    It can be hidden
    Parameter:
      target_CS_WE,parent_CS_WE {str|WebElement} : css selector or WebElement
    Returns:
      {bool}
    '''
    return True if self.__finder.find(target_CS_WE,parent_CS_WE) else False

  @StateDeco('is_displayed')
  def is_displayed(self,target_CS_WE,parent_CS_WE=None):
    '''
    If the connected Element is displayed or not displayed on a webpage
    Parameter:
      target_CS_WE,parent_CS_WE {str|WebElement} : css selector or WebElement
    Returns:
      {bool}
    '''
    web_element = self.__finder.find(target_CS_WE,parent_CS_WE)
    if not web_element:
      return False
    return web_element.is_displayed()

  @StateDeco('is_enabled')
  def is_enabled(self,target_CS_WE,parent_CS_WE=None):
    '''
    If the connected Element is enabled or disabled on a webpage
    Parameter:
      target_CS_WE,parent_CS_WE {str|WebElement} : css selector or WebElement
    Returns:
      {bool}
    '''
    web_element = self.__finder.find(target_CS_WE,parent_CS_WE)
    if not web_element:
      return False
    return web_element.is_enabled()

  @StateDeco('is_selected')
  def is_selected(self,target_CS_WE,parent_CS_WE=None):
    '''
    Detemines if the element is selected or not, widely used on:
      1. check box
      2. radio box
      3. input element
      4. option element
    Parameter:
      target_CS_WE,parent_CS_WE {str|WebElement} : css selector or WebElement
    Returns:
      {bool}
    '''
    web_element = self.__finder.find(target_CS_WE,parent_CS_WE)
    if not web_element:
      return False
    return web_element.is_selected()

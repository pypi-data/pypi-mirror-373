from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.support.relative_locator import locate_with
from .deco.FinderDeco import FinderDeco   

class Finder():
  '''
  Locating the elements based on the provided locator values.
  '''

  def __init__(self,driver):
    self.__driver = driver
  
  # === part 1:  geneal === #
  @FinderDeco('find')
  def find(self,target_CS_WE,parent_CS_WE=None):
    '''
    First matching element
    Get the first element in the DOM that matches with the provided locator.
    Parameter:
      target_CS_WE {str|WebElement} : the target element's css selector or WebElement
      parent_CS_WE {str|WebElement} : the parent element's css selector or WebElement
        - By default: the parent is the driver (the entire DOM)
    @returns {WebElement}
    '''
    if type(target_CS_WE) == WebElement:
      return target_CS_WE
    
    parent_WE = self.__get_parent_WE(parent_CS_WE)
    dom_set = parent_WE if parent_WE else self.__driver

    try:
      return self.__find_by_CS(target_CS_WE,dom_set)
    except Exception as e:
      return None

  @FinderDeco('find_all')
  def find_all(self,target_CS_WE,parent_CS_WE=None):
    '''
    All matching elements
    There are several use cases for needing to get references to all elements that match a locator, rather than just the first one. 
    Parameter:
      target_CS_WE {str|WebElement} : the target element's css selector or WebElement
      parent_CS_WE {str|WebElement} : the parent element's css selector or WebElement
        - By default: the parent is the driver (the entire DOM)
    @returns {list<WebElement>}
    '''

    if type(target_CS_WE) == WebElement:
      return [target_CS_WE]
    
    parent_WE = self.__get_parent_WE(parent_CS_WE)
    dom_set = parent_WE if parent_WE else self.__driver

    try:
      return self.__find_all_by_CS(target_CS_WE,dom_set)
    except Exception as e:
      return None

  # === part 2:  get shadow element === #
  @FinderDeco('find_shadow')
  def find_shadow(self,target_CS_WE,parent_CS_WE):
    '''
    Find the element in shadow root
    Parameter:
      target_CS_WE {str} : css selector of the element in the shadow root
      parent_CS_WE {str|WebElement} : the element contains the shadow root
    '''
    shadow_host = self.__get_parent_WE(parent_CS_WE)
    shadow_root = shadow_host.shadow_root
    return shadow_root.find_element(By.CSS_SELECTOR,target_CS_WE)

  # === part 3:  get element by link text === #
  def find_by_link(self,link_text,parent_CS_WE):
    '''
    @description : 根据 a元素的内容查找元素
     - 不受隐藏在在屏外限制
     - 如果不在屏内，会自动滚动到屏内
    @param {str} link_text ：链接内可视文本
    '''
    parent_WE = self.__get_parent_WE(parent_CS_WE)
    dom_set = parent_WE if parent_WE else self.__driver
    return dom_set.find_element(By.LINK_TEXT,link_text)

  def find_by_partial_link(self,link_text):
    return self.__driver.find_element(By.PARTIAL_LINK_TEXT,link_text)

  # === part 4:  get element by other element postion === #
  def above(self,target_CS,anchor_CS):
    '''
    Find the target element above the anhcor element
    Parameter:
      target_CS {str} : the target element's selector, general is a tag selector
      anchor_CS {str} : the anchor element's selector
    Returns:
      {WebElement]
    '''
    locator = locate_with(By.CSS_SELECTOR,target_CS).above({By.CSS_SELECTOR:anchor_CS})
    return self.__driver.find_element(locator)

  def below(self,target_CS,anchor_CS):
    locator = locate_with(By.CSS_SELECTOR,target_CS).below({By.CSS_SELECTOR:anchor_CS})
    return self.__driver.find_element(locator)

  def left(self,target_CS,anchor_CS):
    locator = locate_with(By.CSS_SELECTOR,target_CS).to_left_of({By.CSS_SELECTOR:anchor_CS})
    return self.__driver.find_element(locator)

  def right(self,target_CS,anchor_CS):
    locator = locate_with(By.CSS_SELECTOR,target_CS).to_right_of({By.CSS_SELECTOR:anchor_CS})
    return self.__driver.find_element(locator)

  def near(self,target_CS,anchor_CS):
    '''
    you can use the near method to identify an element that is at most 50px away from the provided locator
    '''
    locator = locate_with(By.CSS_SELECTOR,target_CS).near({By.CSS_SELECTOR:anchor_CS})
    return self.__driver.find_element(locator)

  # === appendix:  private methods === #
  def __get_parent_WE(self,parent_CS_WE):
    if not parent_CS_WE:
      return None

    if type(parent_CS_WE) == WebElement:
      dom_set = parent_CS_WE
    elif type(parent_CS_WE) == str:
      dom_set = self.__find_by_CS(parent_CS_WE,self.__driver)

    return dom_set

  def __find_by_CS(self,CS,dom_set):
    return dom_set.find_element(By.CSS_SELECTOR,CS)

  def __find_all_by_CS(self,CS,dom_set):
    return dom_set.find_elements(By.CSS_SELECTOR,CS)

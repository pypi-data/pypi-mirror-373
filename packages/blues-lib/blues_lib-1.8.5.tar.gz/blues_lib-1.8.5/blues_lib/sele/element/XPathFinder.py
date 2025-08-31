from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By

class XPathFinder():

  '''
  Locating the elements based on the provided locator values.
  '''

  def __init__(self,driver):
    self.__driver = driver
  
  # === part 1:  get element by text === #
  def find(self, target_xpath:str, parent_element:WebElement=None) -> WebElement:

    """
    根据xpath查找元素，可指定父级选择器
    
    :param target_xpath: 要查找的xpath
    :param parent_element: 父级元素，默认为None表示从根元素开始查找
    :return: 找到的WebElement对象
    """
    # 拼接XPath，先定位父级再在其内部查找包含指定文本的元素
    return self._find_by_xpath(target_xpath,parent_element)

  def find_all(self, target_xpath:str, parent_element:WebElement=None) -> list[WebElement]:

    """
    根据xpath查找所有元素，可指定父级选择器
    
    :param target_xpath: 要查找的xpath
    :param parent_element: 父级元素，默认为None表示从根元素开始查找

    :return: 找到的WebElement对象列表
    """
    return self._find_all_by_xpath(target_xpath,parent_element)


  # === appendix:  private methods === #
  def _find_by_xpath(self,xpath,parent_element:WebElement=None):
    try:
      if parent_element:
        return parent_element.find_element(By.XPATH,xpath)
      else:
        return self.__driver.find_element(By.XPATH,xpath)
    except:
      return None


  def _find_all_by_xpath(self,xpath,parent_element:WebElement=None):
    try:
      if parent_element:
        return parent_element.find_elements(By.XPATH,xpath)
      else:
        return self.__driver.find_elements(By.XPATH,xpath)
    except:
      return None

from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions 
from .deco.ECTextDeco import ECTextDeco
from .deco.ECElementTextDeco import ECElementTextDeco
from .deco.ECElementDeco import ECElementDeco
from .deco.ECBaseDeco import ECBaseDeco

class EC():
  '''
  official expected_conditions
  https://www.selenium.dev/selenium/docs/api/py/webdriver_support/selenium.webdriver.support.expected_conditions.html
  '''

  def __init__(self,driver):
    self.__driver = driver

  #-- module 1: wait for title --#
  @ECTextDeco('title_is')
  def title_is(self,title,timeout=5):  
    '''
    @description : Determines whether the document title is equal to a string
    @param {str} title : the compare string
    @param {int} timeout : Maximum waiting time
    @returns {true|None}
    '''
    wait_func = expected_conditions.title_is(title)
    return self.__wait(wait_func,timeout)
  
  @ECTextDeco('title_contains')
  def title_contains(self,title,timeout=5):  
    '''
    @description : Determines whether the document title contains a string
    @param {str} title : the compare string
    @param {int} timeout : Maximum waiting time
    @returns {true|None}
    '''
    wait_func = expected_conditions.title_contains(title)
    return self.__wait(wait_func,timeout)

  #-- module 2: wait for url --#
  @ECTextDeco('url_contains')
  def url_contains(self,url_slice:str,timeout=5):
    '''
    @description : if the current_url contains a substring
    @param {str} url_slice : the url's substring
    @param {int} timeout : Maximum waiting time
    @returns {bool}
    '''
    wait_func = expected_conditions.url_contains(url_slice)
    return self.__wait(wait_func,timeout)

  @ECTextDeco('url_matches')
  def url_matches(self,url_pattern:str,timeout=5):
    '''
    @description : if the current_url matches the regexp pattern
      - only need to match the substring, not the whole url
    @param {str} url_pattern : the url's regexp pattern
    @param {int} timeout : Maximum waiting time
    @returns {bool}
    '''
    wait_func = expected_conditions.url_matches(url_pattern)
    return self.__wait(wait_func,timeout)

  @ECTextDeco('url_changes')
  def url_changes(self,url,timeout=5):
    '''
    @description : Compare the current_url with the url
      - The passing url is different from the current_url, will return True.
      - The passing url is the same as the current_url, will return False.
      - It should be noted that the current_url may change automatically after a browser opens a URL. Such as:
        - The HTTP protocol will automatically convert to HTTPS.
        - A slash "/" will be automatically appended to the end of the URL.
    @param {str} url : the compare url
    @param {int} timeout : Maximum waiting time
    @returns {bool}
    '''
    wait_func = expected_conditions.url_changes(url)
    return self.__wait(wait_func,timeout)

  @ECTextDeco('url_to_be')
  def url_to_be(self,url,timeout=5):
    '''
    @description : Compare the current_url with the url
      - The two URLs must be identical.
      - It should be noted that the current_url may change automatically after a browser opens a URL. Such as:
        - The HTTP protocol will automatically convert to HTTPS.
        - A slash "/" will be automatically appended to the end of the URL.
    @param {str} url : the compare url
    @param {int} timeout : Maximum waiting time
    @returns {bool}
    '''
    wait_func = expected_conditions.url_to_be(url)
    return self.__wait(wait_func,timeout)

  @ECTextDeco('window_count_to_be')
  def window_count_to_be(self,count=1,timeout=5):
    '''
    @description : Wait for the number of windows to change to `count`
    @param {int} timeout : Maximum waiting time
    @returns {true|None}
    '''
    wait_func = expected_conditions.number_of_windows_to_be(count)
    return self.__wait(wait_func,timeout)
  
  #-- module 3: wait for presence --#
  @ECElementDeco('to_be_presence')
  def to_be_presence(self,target_CS_WE,timeout=5,parent_WE=None):
    '''
    @description : wait and return the element
    @param {str} CS :  the element's css CS
    @param {int} timeout : Maximum waiting time
    @returns {WebElement|None}
    '''
    locator = (By.CSS_SELECTOR,target_CS_WE)
    wait_func = expected_conditions.presence_of_element_located(locator)
    return self.__wait(wait_func,timeout,parent_WE)

  @ECElementDeco('all_to_be_presence')
  def all_to_be_presence(self,target_CS_WE,timeout=5):
    '''
    @description : wait and return all of elements
    @param {str} CS :  the element's css CS
    @returns {list<WebElement>|None}
    '''
    locator = (By.CSS_SELECTOR,target_CS_WE)
    wait_func = expected_conditions.presence_of_all_elements_located(locator)
    return self.__wait(wait_func,timeout)

  #-- module 4: wait for visible --#
  @ECElementDeco('to_be_visible')
  def to_be_visible(self,target_CS_WE,timeout=5):
    '''
    @description : wait and return the matched vsibile element
      - judge by the css display and visibility property 
      - the element may be out of the viewport
    @param {str} CS :  the element's css CS
    @param {int} timeout : Maximum waiting time
    @returns {WebElement|None}
    '''
    locator = (By.CSS_SELECTOR,target_CS_WE)
    wait_func = expected_conditions.visibility_of_element_located(locator)
    return self.__wait(wait_func,timeout)
  
  @ECElementDeco('all_to_be_visible')
  def all_to_be_visible(self,target_CS_WE,timeout=5):
    '''
    @description : wait (at least one of the matched elements must be visible) and return them
    @param {str} CS :  the element's css CS
    @param {int} timeout : Maximum waiting time
    @returns {list<WebElement>|None}
    '''
    locator = (By.CSS_SELECTOR,target_CS_WE)
    wait_func = expected_conditions.visibility_of_all_elements_located(locator)
    return self.__wait(wait_func,timeout)

  @ECElementDeco('any_to_be_visible')
  def any_to_be_visible(self,target_CS_WE,timeout=5):
    '''
    @description : wait (all of the matched elements must be visible) and return them
    @param {str} CS :  the element's css CS
    @param {int} timeout : Maximum waiting time
    @returns {list<WebElement>|None}
    '''
    locator = (By.CSS_SELECTOR,target_CS_WE)
    wait_func = expected_conditions.visibility_of_any_elements_located(locator)
    return self.__wait(wait_func,timeout)

  @ECElementDeco('to_be_invisible')
  def to_be_invisible(self,target_CS_WE,timeout=5):
    '''
    @description : wait the element invisible or removed, and return bool
    @param {str} CS :  the element's css CS
    @param {int} timeout : Maximum waiting time
    @returns {true|None}
    '''
    locator = (By.CSS_SELECTOR,target_CS_WE)
    wait_func = expected_conditions.invisibility_of_element_located(locator)
    return self.__wait(wait_func,timeout)

  #-- module 5: wait for text and value --#
  @ECElementTextDeco('value_contains')
  def value_contains(self,target_CS_WE,text,timeout=5):
    '''
    @description : Determines whether the value attribute of a element contains a string
    @param {str} CS :  the element's css CS
    @param {str} text : this search string
    @param {int} timeout : Maximum waiting time
    @returns {True|None}
    '''
    locator = (By.CSS_SELECTOR,target_CS_WE)
    wait_func = expected_conditions.text_to_be_present_in_element_value(locator,text)
    return self.__wait(wait_func,timeout)

  @ECElementTextDeco('text_contains')
  def text_contains(self,target_CS_WE,text,timeout=5):
    '''
    @description : Determines whether the text in an element tag contains a string
     - It can be inside a child of an element
    @param {str} CS :  the element's css CS
    @param {str} text : this search string
    @param {int} timeout : Maximum waiting time
    @returns {True|None}
    '''
    locator = (By.CSS_SELECTOR,target_CS_WE)
    wait_func = expected_conditions.text_to_be_present_in_element(locator,text)
    return self.__wait(wait_func,timeout)

  #-- module 6: wait for specific state --#
  @ECElementDeco('to_be_clickable')
  def to_be_clickable(self,target_CS_WE,timeout=5):
    '''
    @description : Determines whether a element exist and visible and clickable
     - disabled button : return false
     - if display and enable, return true
     - judge by the css display and visibility property 
     - the element may be out of the viewport
    @param {str} CS :  the element's css CS
    @param {int} timeout : Maximum waiting time
    @returns {WebElement|None}
    '''
    locator = (By.CSS_SELECTOR,target_CS_WE)
    wait_func = expected_conditions.element_to_be_clickable(locator)
    return self.__wait(wait_func,timeout)

  @ECElementDeco('to_be_selected')
  def to_be_selected(self,target_CS_WE,timeout=5):
    '''
    @description : Determines whether a element exist and visible and selected
     - only can be used to radio and checkbox 
    @param {str} CS :  the element's css CS
    @param {int} timeout : Maximum waiting time
    @returns {True|None}
    '''
    locator = (By.CSS_SELECTOR,target_CS_WE)
    # the method name has keyword `located`
    wait_func = expected_conditions.element_located_to_be_selected(locator)
    return self.__wait(wait_func,timeout)

  #-- module 8: wait for stale --#
  @ECElementDeco('to_be_stale')
  def to_be_stale(self,target_CS_WE,timeout=5):
    '''
    @description : wait a dom element to be removed, the reference will lose efficacy
    @param {str} CS :  the element's css CS
    @param {int} timeout : Maximum waiting time
    @returns {true|None}
    '''
    web_element = self.to_be_presence(target_CS_WE,1)
    if not web_element:
      return True
    wait_func = expected_conditions.staleness_of(web_element)
    return self.__wait(wait_func,timeout)

  #-- module 7: wait for window and frame and alert --#
  @ECBaseDeco('alert_to_be_presence')
  def alert_to_be_presence(self,timeout=5):
    '''
    @description : wait and return the Alert element
    @param {int} timeout : Maximum waiting time
    @returns {Alert|None} 
    '''
    wait_func = expected_conditions.alert_is_present()
    alert = self.__wait(wait_func,timeout)
    return alert
  
  @ECBaseDeco('alert_to_be_closed')
  def alert_to_be_closed(self,timeout=5):
    '''
    Wait and close the alert
    Returns:
      {True}
    '''
    alert = self.alert_to_be_presence(timeout)
    if alert:
      alert.accept()
    return True

  @ECElementDeco('frame_to_be_presence')
  def frame_to_be_switched(self,target_CS_WE,timeout=5):
    '''
    @description : wait and switch to the frame
    @param {str} CS : the frame's css CS
    @param {int} timeout : Maximum waiting time
    @returns {true|None}
    '''
    locator = (By.CSS_SELECTOR,target_CS_WE)
    wait_func = expected_conditions.frame_to_be_available_and_switch_to_it(locator)
    return self.__wait(wait_func,timeout)
  
  @ECTextDeco('window_to_be_presence')
  def window_to_be_opened(self,handles,timeout=5):
    '''
    @description : Wait for new tab/window is opened
    @param {list[str]} : the current handles list
    @param {int} timeout : Maximum waiting time
    @returns {true|None}
    '''
    wait_func = expected_conditions.new_window_is_opened(handles)
    return self.__wait(wait_func,timeout)

  #-- module -1: helper method --#
  def __wait(self,wait_func,timeout=5,parent_WE=None):
    '''
    Create the format EC getter return value
    Don't throw errors
    Parameter:
      wait_func {function} : the ec function
      timeout {int} : the maximum waiting seconds
    Returns:
      {WebElement | list<WebElement> | None}
    '''
    try:
      root_node = parent_WE if parent_WE else self.__driver
      return WebDriverWait(root_node,timeout=timeout).until(wait_func)
    except Exception as e:
      # Some conditions will throw a TimeoutException or return false
      return False

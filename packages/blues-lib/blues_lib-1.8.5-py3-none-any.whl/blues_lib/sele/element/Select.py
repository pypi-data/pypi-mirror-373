import sys,os,re
from selenium.webdriver.support.select import Select as DriverSelect
from selenium.webdriver.remote.webelement import WebElement
from .deco.SelectDeco import SelectDeco
from .deco.SelectKeyDeco import SelectKeyDeco

sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from sele.waiter.Querier import Querier  
from sele.element.Info import Info  

# 提供下拉选择相关功能
class Select():
  '''
  That this class only works for HTML elements select and option. 
  It is possible to design drop-downs with JavaScript overlays using div or li, and this class will not work for those
  '''
 
  def __init__(self,driver):
    self.__driver = driver
    self.__querier = Querier(driver,1)
    self.__info = Info(driver)
  
  def get(self,target_CS_WE,parent_CS_WE=None,timeout=5):
    '''
    Return the Select instance
    Parameter:
      target_CS_WE,parent_CS_WE {str|WebElement} : the html select element cess selector or web element
    Returns:
      {Select}
    '''
    web_element = self.__querier.query(target_CS_WE,parent_CS_WE,timeout)
    if not web_element:
      return None
    return DriverSelect(web_element)
  
  @SelectDeco('get_options')
  def get_options(self,target_CS_WE,parent_CS_WE=None,timeout=5):
    '''
    @description 获取select选项/选中对象list
    @param {str} target_CS_WE,parent_CS_WE
    @returns {list<dict>}
      [{'value': 'volvo', 'label': '沃尔沃'}]
    '''
    options = self.__get_options(target_CS_WE,parent_CS_WE,timeout)
    return self.__get_option_items(options)
      
  @SelectDeco('geted_options')
  def get_selected_options(self,target_CS_WE,parent_CS_WE=None,timeout=5):
    '''
    @returns {list<dict>}
      [{'value': 'volvo', 'label': '沃尔沃'}]
    '''
    options = self.__get_options(target_CS_WE,'all_selected_options',parent_CS_WE,timeout)
    return self.__get_option_items(options)

  @SelectDeco('get_frist_selected_option')
  def get_first_selected_option(self,target_CS_WE,parent_CS_WE=None,timeout=5):
    '''
    @returns {dict}
      {'value': 'volvo', 'label': '沃尔沃'}
    '''
    options = self.__get_options(target_CS_WE,'first_selected_option',parent_CS_WE,timeout)
    return self.__get_option_items(options)

  def __get_options(self,target_CS_WE,stat=None,parent_CS_WE=None,timeout=5):
    select = self.get(target_CS_WE,parent_CS_WE,timeout)
    if not select:
      return None
    if stat == 'all_selected_options':
      return select.all_selected_options
    elif stat == 'first_selected_option':
      return select.first_selected_option
    else:
      return select.options

  def __get_option_items(self,option_elements):
    if not option_elements:
      return None
    
    # first selected option
    if type(option_elements) == WebElement:
      return {
        'value':option_elements.get_attribute('value'),
        'text':option_elements.text,
      }

    items = []
    for option in option_elements:
      items.append({
        'value':option.get_attribute('value'),
        'text':option.text,
      })
    return items

  @SelectKeyDeco('select_by_index')
  def select_by_index(self,target_CS_WE,index,parent_CS_WE=None,timeout=5):
    '''
    Select a option by index
    Parameter:
      index {int} : the option's index
      target_CS_WE {str|WebElement} : the select element
      parent_CS_WE {str|WebElement} : the select's parent element
    Returns:
      {None}
    '''
    select = self.get(target_CS_WE,parent_CS_WE,timeout)
    if not select:
      return False

    indexs = index if type(index)==list else [index]
    for idx in indexs:
      select.select_by_index(idx)

    return len(indexs)
  
  @SelectKeyDeco('select_by_value')
  def select_by_value(self,target_CS_WE,value,parent_CS_WE=None,timeout=5):
    '''
    Selet multi values
    '''
    select = self.get(target_CS_WE,parent_CS_WE,timeout)
    if not select:
      return False

    values = value if type(value)==list else [value]
    for val in values:
      select.select_by_value(val)

    return len(values)

  @SelectKeyDeco('select_by_value_or_text')
  def select_by_value_or_text(self,target_CS_WE,value,parent_CS_WE=None,timeout=5):
    '''
    Selet multi values
    '''
    web_element = self.__querier.query(target_CS_WE,parent_CS_WE,timeout)
    if not web_element:
      return None

    select = self.get(web_element)

    values = value if type(value)==list else [value]
    
    first_option_html = self.__info.get_outer_html('option',web_element)

    if re.search(r'value\s*=',first_option_html):  
      for val in values:
        select.select_by_value(val)
    else:
      for val in values:
        select.select_by_visible_text(val)

    return len(values)

  @SelectKeyDeco('select_by_text')
  def select_by_text(self,target_CS_WE,text,parent_CS_WE=None,timeout=5):
    '''
    Returns:
      {None}
    '''
    select = self.get(target_CS_WE,parent_CS_WE,timeout)
    if not select:
      return False

    texts = text if type(text)==list else [text]
    for txt in texts:
      select.select_by_visible_text(txt)

    return len(texts)

  @SelectDeco('deselect_all')
  def deselect_all(self,target_CS_WE,parent_CS_WE=None,timeout=5):
    '''
    You may only deselect all options of a multi-select
    Returns:
      {None}
    '''
    select = self.get(target_CS_WE,parent_CS_WE,timeout)
    if not select:
      return False
    if not select.is_multiple:
      return False
    return select.deselect_all()
    
  @SelectKeyDeco('deselect_by_index')
  def deselect_by_index(self,target_CS_WE,index,parent_CS_WE=None,timeout=5):
    '''
    Returns:
      {None}
    '''
    select = self.get(target_CS_WE,parent_CS_WE,timeout)
    if not select:
      return False
    if not select.is_multiple:
      return False

    indexs = index if type(index)==list else [index]
    for idx in indexs:
      select.deselect_by_index(idx)

    return len(indexs)
  
  @SelectKeyDeco('deselect_by_value')
  def deselect_by_value(self,target_CS_WE,value,parent_CS_WE=None,timeout=5):
    '''
    Returns:
      {None}
    '''
    select = self.get(target_CS_WE,parent_CS_WE,timeout)
    if not select:
      return False
    if not select.is_multiple:
      return False

    values = value if type(value)==list else [value]
    for val in values:
      select.deselect_by_value(val)

    return len(values)

  @SelectKeyDeco('deselect_by_text')
  def deselect_by_text(self,target_CS_WE,text,parent_CS_WE=None,timeout=5):
    '''
    Returns:
      {None}
    '''
    select = self.get(target_CS_WE,parent_CS_WE,timeout)
    if not select:
      return False
    if not select.is_multiple:
      return False

    texts = text if type(text)==list else [text]
    for txt in texts:
      select.deselect_by_visible_text(txt)

    return len(texts)

  @SelectDeco('is_multiple')
  def is_multiple(self,target_CS_WE,parent_CS_WE=None,timeout=5):
    '''
    Returns:
      {true|None}
    '''
    select = self.get(target_CS_WE,parent_CS_WE,timeout)
    if not select:
      return False
    return select.is_multiple




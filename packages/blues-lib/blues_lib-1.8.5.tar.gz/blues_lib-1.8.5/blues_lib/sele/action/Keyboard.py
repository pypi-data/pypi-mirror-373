import sys,os,re,time
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from sele.waiter.Querier import Querier
from sele.action.Mouse import Mouse


class Keyboard():

  keys={
    'select':Keys.CONTROL+"A",
    'copy':Keys.CONTROL+"C",
    'paste':Keys.CONTROL+"V",
    'cut':Keys.CONTROL+"X", # 拼接为同时使用
    'clear':Keys.DELETE, # 元组元素为依次使用
    'enter':Keys.ENTER,
    'f12':Keys.F12,
    'arrow_down':Keys.ARROW_DOWN,
    'arrow_up':Keys.ARROW_UP,
    'page_down':Keys.PAGE_DOWN,
    'page_up':Keys.PAGE_UP,
    'down':Keys.DOWN,
    'up':Keys.UP,
    'control':Keys.CONTROL,
    'esc':Keys.ESCAPE,
  }

  def __init__(self,driver):
    self.__driver = driver
    self.__querier = Querier(driver)
    self.__mouse = Mouse(driver)
    self.__chains = ActionChains(driver)

  # == module 1 : function commbo keys == #
  def control(self,target_CS_WE,key='',parent_CS_WE=None):
    '''
    @description : control + () shortcut 
     - Before executing a shortcut command, you must select an input field to gain focus
     - There must be a delay between multiple control instructions, otherwise they are invalid
    '''

    web_element = self.__querier.query(target_CS_WE,parent_CS_WE)
    if not web_element:
      return
    # Make the element explicit in the window
    #self.__mouse.move_into(web_element)
    # must foucs a element first
    self.__mouse.click(web_element)
    self.__chains \
        .key_down(self.keys['control']) \
        .pause(1) \
        .send_keys(key) \
        .pause(1) \
        .key_up(self.keys['control']) \
        .perform()

  # == module 2 : text operation == #
  def select(self,target_CS_WE,parent_CS_WE=None):
    web_element = self.__querier.query(target_CS_WE,parent_CS_WE)
    if not web_element:
      return

    # the element will roll in to viewport automatically
    web_element.send_keys(self.keys['select'])
    return web_element

  def focus(self,target_CS_WE,parent_CS_WE=None):
    web_element = self.__querier.query(target_CS_WE,parent_CS_WE)
    if not web_element:
      return
    # the element will roll in to viewport 
    self.__mouse.click(web_element)
    return web_element

  def copy(self,target_CS_WE,parent_CS_WE=None):
    web_element = self.select(target_CS_WE,parent_CS_WE)
    web_element.send_keys(self.keys['copy'])
    return web_element

  def cut(self,target_CS_WE,parent_CS_WE=None):
    web_element = self.__querier.query(target_CS_WE,parent_CS_WE)
    if not web_element:
      return
    web_element.send_keys(self.keys['cut'])
    return web_element

  def paste(self,target_CS_WE,parent_CS_WE=None):
    web_element = self.__querier.query(target_CS_WE,parent_CS_WE)
    if not web_element:
      return
    self.select(web_element)
    web_element.send_keys(self.keys['paste'])
    return web_element
  
  def paste_after(self,target_CS_WE,parent_CS_WE=None):
    web_element = self.__querier.query(target_CS_WE,parent_CS_WE)
    if not web_element:
      return
    self.focus(web_element)
    web_element.send_keys(self.keys['paste'])
    return web_element

  def clear(self,target_CS_WE,parent_CS_WE=None):
    web_element = self.select(target_CS_WE,parent_CS_WE)
    web_element.send_keys(self.keys['clear'])
    return web_element

  # == module 3 : single key == #
  def enter(self,target_CS_WE,parent_CS_WE=None):
    # must set a target_CS_WE or enter event is noneffective
    web_element = self.select(target_CS_WE,parent_CS_WE)
    web_element.send_keys(self.keys['enter'])
    return web_element
  
  def f12(self,target_CS_WE,parent_CS_WE=None):
    web_element = self.focus(target_CS_WE,parent_CS_WE)
    web_element.send_keys(self.keys['f12'])
    return web_element
  
  def esc(self):
    web_element = self.__querier.query('body')
    web_element.send_keys(self.keys['esc'])
    return web_element
  
  # == module 4 : arrow operation == #
  def arrow_up(self,count=1,interval=1):
    '''
    @description : press arrow up
    @param {int} count : how many times to move
    @param {init} interval : The interval time between moves
    '''
    for i in range(count):
      if interval:
        time.sleep(interval)
      self.__chains.send_keys(self.keys['arrow_up']).perform()

  def arrow_down(self,count=1,interval=1):
    for i in range(count):
      if interval:
        time.sleep(interval)
      self.__chains.send_keys(self.keys['arrow_down']).perform()
  
  def page_up(self,count=1,interval=1):
    for i in range(count):
      if interval:
        time.sleep(interval)
      self.__chains.send_keys(self.keys['page_up']).perform()

  def page_down(self,count=1,interval=1):
    for i in range(count):
      if interval:
        time.sleep(interval)
      self.__chains.send_keys(self.keys['page_down']).perform()

  def up(self,count=1,interval=1):
    '''
    Move like arrow up
    '''
    for i in range(count):
      if interval:
        time.sleep(interval)
      self.__chains.send_keys(self.keys['up']).perform()

  def down(self,count=1,interval=1):
    '''
    Move like arrow down
    '''
    for i in range(count):
      if interval:
        time.sleep(interval)
      self.__chains.send_keys(self.keys['down']).perform()

  # == module 5 : arrow operation in context == #
  def select_context_option(self,target_CS_WE,index=0):
    '''
    @description : right click and select a menu to enter
    @param {str} target_CS_WE : the element where right click
    @param {int} index : the selected menu index
    '''
    if index<=0:
      return
    web_element = self.__querier.query(target_CS_WE)
    self.__chains.context_click(web_element).perform()
    self.down(index)
    self.enter()

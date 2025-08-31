import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from util.BluesType import BluesType 
from type.file.File import File   

class Window():
 
  def __init__(self,driver):
    self.__driver = driver

  # == module 1: set window size == #  
  def maximize(self):
    self.__driver.maximize_window()

  def minimize(self):
    self.__driver.minimize_window()

  def fullscreen(self):
    '''
    Maximize and hide the top tool bar
    '''
    self.__driver.fullscreen_window()

  # == module 2: window screenshot == #  
  def screenshot(self,file_path='')->str:
    '''
    Take screenshot and save as image
    Parameter:
      file_path {str} : local download file path
    Returns:
      {str} : the download file path
    '''
    default_path = self.__get_default_file()

    shot_path = file_path if file_path else default_path
    stat = self.__driver.save_screenshot(shot_path)

    return shot_path if stat else ''

  def __get_default_file(self,prefix='screenshot'):
    dl_dir = File.get_dir_path('screenshot') # 已经包含尾部目录分割线
    filename = File.get_file_name(prefix=prefix,extension='png')
    return os.path.join(dl_dir,filename)

  # == module 3: set/get window size == #  
  def get_size(self):
    '''
    Get the window size
    Returns:
      {dict} : the size dict, like:
        - {'width': 1755, 'height': 946}
    '''
    return self.__driver.get_window_size()

  def set_size(self,width,height):
    '''
    Set the window size
    Paraeter:
      width {int} : window's width
      height {int} : window's height
    Returns:
      {None}
    '''
    self.__driver.set_window_size(width,height)

  # == module 4: set/get window position == #  
  def get_position(self):
    '''
    Get the window's position
    Returns:
      {dict} : the position dict,like:
        - {'x': 99, 'y': 49}
    '''
    return self.__driver.get_window_position()
     
  def set_position(self,x,y):
    '''
    Get the window's position
    Parameter:
      {int} x : the distance between the window's left border to the screen's left border
      {int} y : the distance between the window's top border to the screen's top border
    '''
    self.__driver.set_window_position(x,y)

  # == module 5: get handle info == #  
  def get_handle(self):
    '''
    Get the current window id
    Returns:
      {str} ： handle id, like:
        - '3D31BF6D96E5671253E70BCF33DC7F39'
    '''
    return self.__driver.current_window_handle

  def get_handles(self):
    '''
    Get all window's handles
    Returns:
      {list<str>} ： handles list, like:
        - ['3D31BF6D96E5671253E70BCF33DC7F39']
    '''
    return self.__driver.window_handles

  def get_latest_handle(self):
    '''
    Get the latest opened window
    '''
    return self.get_handles()[-1]

  # == module 6: open new window and switch to it  automactially (selenium v4 api) == #  
  def new_window(self,url=''):
    self.__driver.switch_to.new_window('window')
    if url:
      self.__driver.get(url)
      
  def new_tab(self,url=''):
    '''
    Open a new tab / new window and switch to it automatically
    Parameter:
      {str} url : the url will be opened by the new window
    '''
    self.__driver.switch_to.new_window('tab')
    if url:
      self.__driver.get(url)
      
  # == module 7: toggle window == #  
  def switch_to(self,handle_id):
    '''
    Switch to the specified window
    Parameter:
      handle_id {string} 
    Returns:
      {None}
    '''
    self.__driver.switch_to.window(handle_id)

  def switch_to_latest(self):
    '''
    @description : switch window to the latest opened tab
    '''
    latest_handle = self.get_latest_handle()
    current_handle = self.get_handle()
    if latest_handle != current_handle:
      self.switch_to(latest_handle)
  
  def switch_to_default(self):
    '''
    Click a href and open a tab automatically, wouldn't switch the handle
    But the chrome's view toggle to the new tab
    Need switch back manually
    '''
    handles = self.get_handles()
    self.switch_to(handles[0])

  def switch_to_prev(self):
    '''
    @description : switch window to the prev tab
    '''
    handles = self.get_handles()
    current_handle = self.get_handle()
    current_handle_index = BluesType.last_index(handles,current_handle)
    if current_handle_index>0:
      prev_handle = handles[current_handle_index-1]
      self.switch_to(prev_handle)

  def switch_to_next(self):
    '''
    @description : switch window to the prev tab
    '''
    handles = self.get_handles()
    current_handle_index = BluesType.last_index(handles,self.get_handle())
    if current_handle_index<len(handles)-1:
      next_handle = handles[current_handle_index+1]
      self.switch_to(next_handle)

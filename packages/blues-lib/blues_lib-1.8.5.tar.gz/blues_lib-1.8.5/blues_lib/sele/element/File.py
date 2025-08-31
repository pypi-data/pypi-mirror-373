import sys,os,re,time
from .deco.InfoKeyDeco import InfoKeyDeco
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from sele.waiter.Querier import Querier  
from sele.element.Info import Info  
from util.BluesFiler import BluesFiler
from util.BluesDateTime import BluesDateTime

class File():

  def __init__(self,driver):
    self.__driver = driver
    self.__querier = Querier(driver,5) 
    self.__info = Info(driver) 

  def write(self,target_CS_WE,value,wait_time=3,parent_CS_WE=None,timeout=5):
    '''
    Add one or multiple files to the file input
    If there are multiple files, the upload mode is controlled based on whether multiple file upload is supported
    '''

    files = value if type(value) == list else [value]
    # Supports uploading multiple images at a time
    exist_files = BluesFiler.filter_exists(files)
    web_element = self.__querier.query(target_CS_WE,parent_CS_WE,timeout)
    if not exist_files or not web_element:
      return

    is_multiple = self.__info.get_attr(web_element,'multiple')
    if is_multiple:
      # must join the file paths by \n
      file_lines = '\n'.join(exist_files)
      web_element.send_keys(file_lines)
      BluesDateTime.count_down({'duration':wait_time,'title':'Wait image upload...'})
    else:
      for exist_file in exist_files:
        web_element.send_keys(exist_file)
        BluesDateTime.count_down({'duration':wait_time,'title':'Wait image upload...'})


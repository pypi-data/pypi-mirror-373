import sys,os,re,time
from .deco.InfoKeyDeco import InfoKeyDeco
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from sele.waiter.Querier import Querier  
from type.file.File import File

class Shot():

  def __init__(self,driver):
    self.__driver = driver
    self.__querier = Querier(driver,5) 

  # == module 2: element shot == #
  @InfoKeyDeco('screenshot')
  def screenshot(self,target_CS_WE,file,parent_CS_WE=None,timeout=5):
    '''
    @description 指定元素截图,不支持base64格式
    @param {str} selector : css selector 
    @param {str} file 保存位置
    @returns {str} file_path
    '''
    file_path = file if file else self.__get_default_file()
    web_element = self.__querier.query(target_CS_WE,parent_CS_WE,timeout)
    shot_status = web_element.screenshot(file_path)
    return file_path if shot_status else ''

  def __get_default_file(self,prefix='elementshot'):
    dir_path = File.get_dir_path('screenshot') 
    file_name = File.get_file_name(prefix=prefix,extension='png')
    return os.path.join(dir_path,file_name)

  

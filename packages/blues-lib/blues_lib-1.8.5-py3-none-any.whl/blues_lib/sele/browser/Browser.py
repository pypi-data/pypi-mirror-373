import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
# sele
from sele.interactor.Interactor import Interactor  
from sele.element.Element import Element  
from sele.waiter.Waiter import Waiter  
from sele.action.Action import Action  
from util.BluesFiler import BluesFiler  
from util.BluesConsole import BluesConsole

from type.file.File import File
from logger.LoggerFactory import LoggerFactory

# script
from sele.script.Script import Script 

# parse
from sele.parser.BluesParser import BluesParser  

class Browser():

  def __init__(self,driver):
    self.driver = driver
    self.interactor = Interactor(driver)  
    self.element = Element(driver)  
    self.waiter = Waiter(driver)  
    self.action = Action(driver)  
    self.script = Script(driver)  
    self.parser = BluesParser(driver)  
    self._logger = LoggerFactory({'name':f'{self.__class__.__module__}.{self.__class__.__name__}'}).create_file()

  def open(self,url):
    self.interactor.navi.open(url)
      
  def quit(self):
    self.interactor.navi.quit()

  def read_cookies(self,cookie_file=''):
    file_path = cookie_file if cookie_file else self._get_default_file('json')
    cookies = BluesFiler.read_json(file_path)
    if cookies:
      self._logger.info(f'Managed to read cookies from {file_path}')
    else:
      self._logger.error(f'Failed to read cookies from {file_path}')
    return cookies

  def write_cookies(self,cookies,cookie_file='')->str:
    file_path = cookie_file if cookie_file else self._get_default_file('json')
    is_writed = BluesFiler.write_json(file_path,cookies)

    if is_writed:
      self._logger.info(f'Managed to write cookies to {file_path}')
      return file_path
    else:
      self._logger.error(f'Failed to write cookies to {file_path}')
      return ''

  def _get_default_file(self,extension='txt'):
    current_url = self.interactor.document.get_url()
    default_file = File.get_domain_file_path(current_url,'cookie',extension)
    return default_file 

  def save_cookies(self,cookie_file=''):
    '''
    Save cookies to a file
    @returns {str} : the local file path
    '''
    cookies = self.driver.get_cookies()
    if cookies:
      return self.write_cookies(cookies,cookie_file)
    else:
      BluesConsole.info('Failed to get cookies')
      return ''

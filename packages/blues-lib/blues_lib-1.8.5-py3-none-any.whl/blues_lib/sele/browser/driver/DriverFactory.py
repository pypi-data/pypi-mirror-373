import sys,os,re

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from .args.ChromeArgsFactory import ChromeArgsFactory

sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from config.ConfigManager import config
from logger.LoggerFactory import LoggerFactory

LoggerFactory.set('WDM','info') # 注意名称是 WDM
from webdriver_manager.chrome import ChromeDriverManager


class DriverFactory():

  __taobao_mirror = "https://npm.taobao.org/mirrors/chromedriver" # https://npmmirror.com/mirrors/chromedriver
  __log_level = '0' # 关闭 Driver Manager 的日志输出，减少 I/O 开销。
  __cache_days = '100' # Driver缓存100天
  __page_load_timeout = 20 # 页面加载超时时间
  
  def __init__(self,
    std_args=None,
    exp_args=None,
    cdp_args=None,
    sel_args=None,
    ext_args=None,
    executable_path=None,
    web_driver=None,
    capabilities=None,
    ):
    '''
    @param {dict} std_args
    @param {dict} exp_args
    @param {dict} cdp_args
    @param {dict} sel_args
    @param {dict} ext_args
    @param {dict} grid_capabilities : the grid remote capability dict
    '''
    self.__executable_path = executable_path
    self.__web_driver = web_driver if web_driver else webdriver
    self.__arg_dict = ChromeArgsFactory(std_args,exp_args,cdp_args,sel_args,ext_args).create()
    self.__capabilities = capabilities
    
  def create(self):
    '''
    Get the webdirver
    @param {'manager'|'path'|'env'} service_mode
    '''
    if not self.__executable_path or self.__executable_path == 'manager':
      return self.__create_by_manager()
    elif self.__executable_path == 'env':
      return self.__create_by_env()
    elif self.__executable_path == 'config':
      return self.__create_by_config()
    else:
      return self.__create_by_path()

  def __create_by_manager(self):
    os.environ["WDM_LOG_LEVEL"] = self.__log_level 
    os.environ['WDM_CACHE_VALID_DAYS'] = self.__cache_days
    executable_path = ChromeDriverManager(url=self.__taobao_mirror).install()
    service = Service(executable_path) 
    return self.__get_driver(service)

  def __create_by_config(self):
    executable_path = config.get("webdriver.path")
    service = Service(executable_path) 
    return self.__get_driver(service)

  def __create_by_path(self):
    '''
    @param {str} : the local driver path
    '''
    service = Service(self.__executable_path) 
    return self.__get_driver(service)

  def __create_by_env(self):
    '''
    @description : Create the Chrome driver instance
      - set the driver path as the system env variable
      - It's unstable, and sometimes the macOS system can't establish a connection. 
    '''
    return self.__get_driver()

  def __get_options(self):
    options = Options()
    self.__set_options(options)
    self.__set_capability(options)
    return options
  
  def __set_capability(self,chrome_options):
    if self.__capabilities:
      for key,value in self.__capabilities.items():
        chrome_options.set_capability(key,value)
    
  def __get_driver(self,service=None):
    options = self.__get_options()
    if self.__capabilities:
      return self.__get_remote_driver(options)
    else:
      return self.__get_local_driver(service,options)

  def __get_local_driver(self,service,options):
    if service:
      driver =  self.__web_driver.Chrome( service = service, options = options)
    else:
      driver =  self.__web_driver.Chrome( options = options)

    self.__set_cdp(driver,self.__arg_dict['cdp'])

    driver.set_page_load_timeout(self.__page_load_timeout)

    return driver

  def __get_remote_driver(self,options):
    driver = self.__web_driver.Remote(
      command_executor = self.__executable_path,
      options = options
    )

    driver.set_page_load_timeout(self.__page_load_timeout)

    return driver

  def __set_options(self,options):
    self.__set_std(options,self.__arg_dict['std'])
    self.__set_exp(options,self.__arg_dict['exp'])
    self.__set_ext(options,self.__arg_dict['ext'])
    self.__set_sel(options,self.__arg_dict['sel'])
    
  def __set_std(self,options,args):
    if args:
      for value in args:
        options.add_argument(value)

  def __set_exp(self,options,args):
    if args:
      for key,value in args.items():
        options.add_experimental_option(key,value)

  def __set_cdp(self,driver,args):
    if args:
      for key,value in args.items():
        driver.execute_cdp_cmd(key,value)

  def __set_ext(self,options,args):
    if args:
      for value in args:
        options.add_extension(value)

  def __set_sel(self,options,args):
    if args:
      for key,value in args.items():
        # just set as the options's attr
        setattr(options,key,value)
        
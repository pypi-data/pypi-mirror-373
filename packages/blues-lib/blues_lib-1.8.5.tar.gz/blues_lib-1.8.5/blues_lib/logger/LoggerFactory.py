import sys,os,re,logging
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.factory.Factory import Factory
from logger.FileLogger import FileLogger
from logger.MailLogger import MailLogger

class LoggerFactory(Factory): 

  LOG_LEVELS = {
    'debug':logging.DEBUG,
    'info':logging.INFO, # will print all system info 
    'warning':logging.WARNING,
    'error':logging.ERROR,
  }

  def __init__(self,config:dict):
    self._config = config
  
  def create_system(self):
    '''
    Get a named logger instance
    @param {str} name : the logger's name, recommand using the module name
    '''
    return logging.getLogger(self._config['name'])
  
  def create_file(self):
    return FileLogger(self._config)

  def create_mail(self):
    return MailLogger(self._config)

  @classmethod 
  def set(cls,name,level='info'):
    '''
    为某个模块设置日志层级，默认是warning，一般为了设置info调试
      - 必须在模块import前设置
    @param {str} name : 包名
      - 可通过遍历确认包名：for name in logging.root.manager.loggerDict:
    '''
    pkg_logger = logging.getLogger(name)  
    pkg_logger.setLevel(cls.LOG_LEVELS[level])      # 允许输出 INFO 及以上级别
    # 可选：添加独立的控制台处理器（避免传播到根日志） - 经测试必须设置
    if not pkg_logger.handlers:
      handler = logging.StreamHandler()
      handler.setFormatter(logging.Formatter("%(name)s - %(message)s"))
      pkg_logger.addHandler(handler)

    # 禁止传播到父记录器（关键！避免被根日志过滤）
    pkg_logger.propagate = False

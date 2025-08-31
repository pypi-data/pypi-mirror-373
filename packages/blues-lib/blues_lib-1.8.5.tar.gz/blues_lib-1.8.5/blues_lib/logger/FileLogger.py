import os,sys,re,logging,datetime
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from util.BluesFiler import BluesFiler 
from material.file.MatFile import MatFile

class FileLogger(): 

  _LOG_LEVELS = {
    'debug':logging.DEBUG,
    'info':logging.INFO, # will print all system info 
    'warning':logging.WARNING,
    'error':logging.ERROR,
  }
  _WIDTH = 100 

  def __init__(self,config={}):
    '''
    @description : set log config
    @param {str} config.directory : Directory for storing logs
    @param {str} config.name : log's topic
    @param {int} config.retention_days : Maximum number of days for storing logs
    @param {str} config.level : The lowest level of log output
      - enum: debug info warning error
    '''
    self._file_name = os.environ.get('OS_LOG_NAME',self.__class__.__name__)
    self._config = self._get_config(config)
    # must create the dir before get the logger
    self._set_dir()
    self._logger = self._get_logger()


  def _get_config(self,config:dict):
    dft = {
      'name':self._file_name, # executor module name
      'directory':MatFile.get_today_log_root(),
      'level':'info',
      'retention_days':7,
    }
    return {**dft,**config} if config else dft
    
  def _set_dir(self):
    # make sure the dir exist
    BluesFiler.makedirs(self._config['directory'])
    # clear log history
    BluesFiler.removefiles(self._config['directory'],self._config['retention_days'])

  def _get_logger(self):

    log_level  = self._LOG_LEVELS[self._config['level']]
    logging.basicConfig(level=log_level)
    logger = logging.getLogger(self._config['name']) # will be show in the formatter as the `name`

    log_file = self._get_log_file()
    formatter = self._get_formatter()
    file_logger = logging.FileHandler(log_file,'a','utf-8')
    file_logger.setFormatter(formatter)
    logger.addHandler(file_logger)
    return logger

  def _get_formatter(self):
    split_line = ''.join(['-' for x in range(self._WIDTH)])
    formatter = split_line+'\n'+'%(levelname)s (%(name)s) %(asctime)s:\n%(message)s'
    return logging.Formatter(formatter)
      
  def _get_log_file(self):
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    log_name = f"{self._file_name}_{today}.log" # using the os file name
    return os.path.join(self._config['directory'],log_name)

  def debug(self,message):
    self._logger.debug(message)

  def info(self,message):
    self._logger.info(message)

  def warning(self,message):
    self._logger.warning(message)
  
  def error(self,message):
    self._logger.error(message)
  
  def split(self,title='', char='='):
    """创建一个醒目的日志分隔栏"""
    padding = (self._WIDTH - len(title) - 2) // 2
    left = char * padding
    right = char * (self._WIDTH - padding - len(title) - 2)
    text = title if title else self._file_name
    
    separator = self._get_separator()
    message = f"\n{left} {text} {right}\n{separator}"
    self.info(message)
    
  def _get_separator(self,char='~'):
    return ''.join([char for x in range(self._WIDTH)])

  @property
  def separator(self):
    return self._get_separator()

  @property
  def file(self):
   return self._get_log_file() 

  def print_file(self):
    title = self.file
    char = '-'
    padding = (self._WIDTH - len(title) - 2) // 2
    left = char * padding
    right = char * (self._WIDTH - padding - len(title) - 2)
    print(f'\n{left} {title} {right}')
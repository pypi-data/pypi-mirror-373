import sys,os,re
from functools import wraps
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from logger.LoggerFactory import LoggerFactory

class LogDeco():
  '''
  Only used to the Acter class's resovle method
  '''
  def __init__(self):
    '''
    Create the decorator
    Has no parameters
    '''
    pass

  def __call__(self,func):
    @wraps(func) 
    def wrapper(this,*arg,**kwargs):

      outcome = func(this,*arg,**kwargs)

      if this.message:
        logger = LoggerFactory({'name':f'{this.__class__.__module__}.{this.__class__.__name__}'}).create_file()
        logger.info(this.message)
      
      return outcome

    return wrapper


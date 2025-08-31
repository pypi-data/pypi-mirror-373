import sys,os,re,time
from functools import wraps
from selenium.webdriver.remote.webelement import WebElement
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from util.BluesConsole import BluesConsole

class SwitchDeco():
  '''
  The switch class base deco: alert / frame / window
  '''

  def __init__(self,caller_class,caller_method,cs_index=None,level=3):
    '''
    Create a special decorator for class waiter.EC 
    Parameter:
      caller_method {str} : the wrappered func's name
      level {int} : the log level
        - 3 error : only error info
        - 2 info : error and info
        - 1 debug : all info
    '''
    self.caller_class = caller_class
    self.caller_method = caller_method
    self.level = level
    # the cs parameter's index in the func
    self.arg_cs_index = cs_index
  
  def __call__(self,func):
    @wraps(func) 
    def wrapper(*args,**kwargs):
      return self.wrapper(func,*args,**kwargs)
    return wrapper

  def wrapper(self,func,*args,**kwargs):

    # execute the wrappered func
    outcome = func(*args,**kwargs)
    finish_msg = self.get_finish_msg(outcome,args)

    # print success msg
    if self.level<=2:
      BluesConsole.info(finish_msg)
    
    # must return the wrappered func's value
    return outcome

  def get_finish_msg(self,outcome,args):
    info = self.get_info(args)
    info.update({ 
      'type':type(outcome).__name__,
      'value': self.get_value(outcome)
    })

    values = (self.caller_class,self.caller_method,info)
    return '[%s.%s] Result %s' % values

  def get_value(self,outcome):
    if not outcome:
      return outcome 
    elif type(outcome) == str:
      if len(outcome)<=30:
        return outcome
      else:
        return outcome[0:30]+'...'
    else:
      return str(outcome)
   
  def get_info(self,args):
    cs = self.get_cs(args)
    info = {}
    if cs:
      info['cs'] = cs
    return info

  def get_cs(self,args):
    index = self.arg_cs_index
    return self.get_cs_title(args,index)

  def get_cs_title(self,args,index):
    if index and len(args)>index:
      CS_WE = args[index]
      if type(CS_WE) == WebElement:
        return 'WebElement %s' % CS_WE.tag_name
      else:
        return CS_WE
    else:
      return None



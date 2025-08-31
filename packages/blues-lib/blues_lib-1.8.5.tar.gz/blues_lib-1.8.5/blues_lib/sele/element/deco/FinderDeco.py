
import sys,os,re,time
from functools import wraps
from selenium.webdriver.remote.webelement import WebElement
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from util.BluesConsole import BluesConsole

class FinderDeco():

  caller_class = 'Finder'

  def __init__(self,caller_method,level=3):
    '''
    Create a special decorator for class waiter.EC 
    Parameter:
      caller_method {str} : the wrappered func's name
      level {int} : the log level
        - 3 error : only error info
        - 2 info : error and info
        - 1 debug : all info
    '''
    self.caller_method = caller_method
    self.level = level 

    # func's args index
    self.arg_cs_index = None
    self.arg_pcs_index = None

    # rewrite the index
    self.set_arg_index()
  
  def __call__(self,func):
    @wraps(func) 
    def wrapper(*args,**kwargs):
      return self.wrapper(func,*args,**kwargs)
    return wrapper

  def set_arg_index(self):
    '''
    Template method
    '''
    self.arg_cs_index = 1
    self.arg_pcs_index = 2

  def wrapper(self,func,*args,**kwargs):
    # execute the wrappered func
    outcome = func(*args,**kwargs)

    msgs = self.get_finish_msg(outcome,args)

    # print success msg
    if outcome and self.level<=2 :
      BluesConsole.success(msgs[0])

    # print failure msg
    if not outcome and self.level<=3 :
      BluesConsole.error(msgs[1])
    
    # must return the wrappered func's value
    return outcome

  def get_finish_msg(self,outcome,args):
    info = self.get_info(args)
    info.update({ 
      'type':type(outcome).__name__,
    })

    values = (self.caller_class,self.caller_method,info)
    s_msg = '[%s.%s] Success %s' % values
    f_msg = '[%s.%s] Failure %s' % values

    return [s_msg,f_msg]
   
  def get_info(self,args):
    cs = self.get_cs(args)
    pcs = self.get_pcs(args)
    info = {}
    if cs:
      info['cs'] = cs
    if pcs:
      info['pcs'] = pcs
    return info

  def get_cs(self,args):
    index = self.arg_cs_index
    return self.get_cs_title(args,index)

  def get_pcs(self,args):
    index = self.arg_pcs_index
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



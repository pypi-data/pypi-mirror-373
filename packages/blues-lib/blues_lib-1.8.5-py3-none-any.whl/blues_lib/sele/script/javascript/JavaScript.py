import requests
from .JSDocument import JSDocument
from .JSEvent import JSEvent
from .JSLoader import JSLoader
from .JSScroll import JSScroll
from .JSJQuery import JSJQuery
from .JSPrinter import JSPrinter 
from .JSAlert import JSAlert 

# 混入更多行为模块
class JavaScript(JSDocument,JSEvent,JSLoader,JSScroll,JSJQuery,JSPrinter,JSAlert):
  
  def __init__(self,driver):
    self.driver = driver

  
  def execute(self,script,*args):
    '''
    @description : execute the script string
    @param {str} script : js script
    @param {tuple} args : the rest args
    @returns {any} The return value of the js script
    '''
    return self.driver.execute_script(script,*args)

    
  def execute_async(self,script,*args):
    '''
    @description : Execute js script asynchronously
    @param {str} script : js script
    @param {tuple} args : the rest args
    @returns {str} The return value of the js script's callback func
    '''
    return self.driver.execute_async_script(script,*args)

  def execute_online(self,url):
    '''
    @description : Execute the js script online
    @param {str} url : the js script file path
    @returns {str} : The return value of the js script
    '''
    if not url:
      return None
    response = requests.get(url = url)
    return self.execute(response.text)
  
  def is_var_available(self,var):
    '''
    @description : Determines whether the variable is available
    @param {str} var : variable name, Support attribute concatenation
     - 'navigator'
     - 'navigator.userAgent'
    @returns {bool}
    '''
    var_name = 'window.%s' % var
    script = "var global_var = %s; return !!global_var;" % var_name
    return self.execute(script)

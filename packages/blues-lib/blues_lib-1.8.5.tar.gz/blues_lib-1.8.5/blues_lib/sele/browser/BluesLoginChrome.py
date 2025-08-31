import sys,os,re,time
from .BluesStandardChrome import BluesStandardChrome   

sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from util.BluesConsole import BluesConsole   

class BluesLoginChrome(BluesStandardChrome):
  '''
  This class is used exclusively to open pages that can only be accessed after login
  There are three ways to complete automatic login:
    1. Login by a cookie string
    2. Login by a cookie file path
    3. Login by the BluesLoginer class
  '''
  def __init__(self,
      std_args=None, # {dict} standard args
      exp_args=None, # {dict} experimentalargs
      cdp_args=None, # {dict} chrome devtools protocal args
      sel_args=None, # {dict} selenium args
      ext_args=None, # {dict} extension args
      executable_path=None, # {str} driver.exe path: 'env' - using the env; 'config' - the local path; 'manager' | None - using the driver manager
    ):
    '''
    Parameter:
      url {str} : the url will be opened
      loginer_or_cookie {Loginer|str} : 
        - when as str: it is the cookie string or local cookie file, don't support relogin
        - when as Loginer : it supports to relogin
      anchor {str} : the login page's element css selector
        some site will don't redirect, need this CS to ensure is login succesfully
    '''
    super().__init__(
      std_args,
      exp_args,
      cdp_args,
      sel_args,
      ext_args,
      executable_path
    )
    
  def login(self,login_url:str,logged_in_url:str,login_element:str,wait_time=5):
    # read cookie need get the domain from the url
    self.open(login_url)

    # read the cookie
    cookies = self.read_cookies() 
    if not cookies:
      BluesConsole.info('Failed to login - no cookies')
      return False

    # add cookie to the browser
    self.interactor.cookie.set(cookies) 
    # Must open the logged in page ,Otherwise, you cannot tell if you have logged in
    self.open(logged_in_url) 
    
    # Check if login successfully
    is_logged_in = self.waiter.ec.to_be_stale(login_element,wait_time)
    if is_logged_in:
      BluesConsole.success('Managed to login by the cookie')
      return True
    else:
      BluesConsole.error('Failed to login with cookies')
      return False



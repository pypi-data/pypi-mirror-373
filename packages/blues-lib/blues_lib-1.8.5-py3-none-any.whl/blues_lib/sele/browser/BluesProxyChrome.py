import sys,os,re
from .Browser import Browser
from .driver.ProxyDriverCreator import ProxyDriverCreator   
from .driver.proxy.ProxyMessage import ProxyMessage    
from .driver.proxy.ProxyMessageVisitor import ProxyMessageVisitor     
from .driver.proxy.ProxyCookieVisitor import ProxyCookieVisitor      

sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from util.BluesFiler import BluesFiler  
from util.BluesConsole import BluesConsole   

class BluesProxyChrome(Browser):
  def __init__(self,
      proxy_config=None, # {dict}
      cookie_config=None, # {dict}
      std_args=None, # {dict} standard args
      exp_args=None, # {dict} experimentalargs
      cdp_args=None, # {dict} chrome devtools protocal args
      sel_args=None, # {dict} selenium args
      ext_args=None, # {dict} extension args
      executable_path=None # {str} driver.exe path: 'env' - using the env; 'xxx' - the local path; None - using the driver manager
    ):
    '''
    Create a proxy browser instance
    @param {dict} proxy_config : the selenium-wire's standard config. The attributes are added to the driver object
      {
        'scopes':['.*baidu.com.*'],
        'request_interceptor': lambda request, 
        'response_interceptor':lambda request,response,
      }
    @param {dict} cookie_config : the cookie's filter pattern
      {
        'url_pattern': 'abc/efg', # the request url regexp pattern
        'value_pattern': 'a=b', # the cookie value's regexp pattern
      }
    '''
    driver = ProxyDriverCreator(
      std_args,
      exp_args,
      cdp_args,
      sel_args,
      ext_args,
      executable_path
    ).create()

    self.__proxy_config = {**proxy_config,
      'request_interceptor': lambda request: (
        # 移除可能暴露代理的请求头
        request.headers.pop('Proxy-Connection', None),
        request.headers.pop('Via', None),
        request.headers.pop('X-Forwarded-For', None),
        request.headers.pop('X-Proxy-ID', None)
      ) 
    }
    self.__cookie_config = cookie_config
    self.__set_proxy(driver)

    super().__init__(driver)

  def __set_proxy(self,driver):
    '''
    Add the standard selenium-wire config to the driver isntance
    '''
    if not self.__proxy_config:
      return
    for key,value in self.__proxy_config.items():
      setattr(driver,key,value)

  def get_messages(self):
    proxy_message = ProxyMessage(self.driver.requests)
    return proxy_message.accept_message_visitor(ProxyMessageVisitor())

  def get_cookies(self):
    cookie_message = ProxyMessage(self.driver.requests)
    return cookie_message.accept_cookie_visitor(ProxyCookieVisitor(self.__cookie_config))

  def save_messages(self,file=''):
    messages = self.get_messages()
    file_path = file if file else self.__get_default_file('json')
    return BluesFiler.write_json(file_path,messages)

  def save_cookies(self,cookie_file=''):
    '''
    Save cookies to a file
    @returns {str} : the local file path
    '''
    cookies = self.get_cookies()
    if cookies:
      return self.write_cookies(cookies,cookie_file)
    else:
      BluesConsole.info('No matched cookie by: %s' % self.__cookie_config)
      return ''

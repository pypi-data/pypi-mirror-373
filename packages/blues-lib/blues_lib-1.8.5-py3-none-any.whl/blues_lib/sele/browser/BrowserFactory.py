from .BluesStandardChrome import BluesStandardChrome
from .BluesHeadlessChrome import BluesHeadlessChrome
from .BluesHeadlessLoginChrome import BluesHeadlessLoginChrome
from .BluesDebugChrome import BluesDebugChrome
from .BluesLoginChrome import BluesLoginChrome
from .BluesProxyChrome import BluesProxyChrome
from .BluesRemoteChrome import BluesRemoteChrome
from .BluesMobileChrome import BluesMobileChrome

class BrowserFactory:
  
  def __init__(self,browser_mode):
    self.__browser_mode = browser_mode

  def create(self,*args,**kwargs):
    if self.__browser_mode == 'standard':
      return BluesStandardChrome(*args,**kwargs)
    elif self.__browser_mode == 'headless':
      return BluesHeadlessChrome(*args,**kwargs)
    elif self.__browser_mode == 'headlesslogin':
      return BluesHeadlessLoginChrome(*args,**kwargs)
    elif self.__browser_mode == 'debug':
      return BluesDebugChrome(*args,**kwargs)
    elif self.__browser_mode == 'login':
      return BluesLoginChrome(*args,**kwargs)
    elif self.__browser_mode == 'proxy':
      return BluesProxyChrome(*args,**kwargs)
    elif self.__browser_mode == 'remote':
      return BluesRemoteChrome(*args,**kwargs)
    elif self.__browser_mode == 'mobile':
      return BluesMobileChrome(*args,**kwargs)
    else:
      return None

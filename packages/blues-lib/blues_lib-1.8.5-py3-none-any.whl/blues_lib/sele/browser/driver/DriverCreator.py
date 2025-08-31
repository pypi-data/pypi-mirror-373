from abc import ABC
from .DriverFactory import DriverFactory    

class DriverCreator(ABC):

  def __init__(self,
      std_args=None, # {dict} standard args
      exp_args=None, # {dict} experimentalargs
      cdp_args=None, # {dict} chrome devtools protocal args
      sel_args=None, # {dict} selenium args
      ext_args=None, # {dict} extension args
      executable_path=None, # {str} driver.exe path: 'env' - using the env; 'xxx' - the local path; None - using the driver manager
      web_driver=None, # {webdriver} selenium webdriver
      capabilities=None, # {dict} grid remote capability
    ):
    self._std_args = std_args if std_args else {}
    self._exp_args = exp_args if exp_args else {}
    self._cdp_args = cdp_args if cdp_args else {}
    self._sel_args = sel_args if sel_args else {}
    self._ext_args = ext_args if ext_args else {}
    self._executable_path = executable_path
    self._web_driver = web_driver
    self._capabilities = capabilities
    
  def create(self):
    '''
    returns {webdriver}
    '''
    factory = DriverFactory(
      self._std_args,
      self._exp_args,
      self._cdp_args,
      self._sel_args,
      self._ext_args,
      self._executable_path,
      self._web_driver,
      self._capabilities,
    )
    return factory.create()
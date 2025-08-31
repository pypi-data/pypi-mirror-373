from .Browser import Browser
from .driver.StandardDriverCreator import StandardDriverCreator  

class BluesRemoteChrome(Browser):

  def __init__(self,
      std_args=None, # {dict} standard args
      exp_args=None, # {dict} experimentalargs
      cdp_args=None, # {dict} chrome devtools protocal args
      sel_args=None, # {dict} selenium args
      ext_args=None, # {dict} extension args
      executable_path=None, # {str} the hub's address
      capabilities=None,
    ):
    
    __capabilities = capabilities if capabilities else {}
    __capabilities['browserName'] = "chrome" 
    driver = StandardDriverCreator(
      std_args,
      exp_args,
      cdp_args,
      sel_args,
      ext_args,
      executable_path,
      capabilities = __capabilities
    ).create()

    super().__init__(driver)
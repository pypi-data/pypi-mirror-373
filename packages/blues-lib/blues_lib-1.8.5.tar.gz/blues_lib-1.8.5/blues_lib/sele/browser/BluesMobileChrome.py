from .Browser import Browser
from .driver.StandardDriverCreator import StandardDriverCreator  

class BluesMobileChrome(Browser):

  def __init__(self,
      std_args=None, # {dict} standard args
      exp_args=None, # {dict} experimentalargs
      cdp_args=None, # {dict} chrome devtools protocal args
      sel_args=None, # {dict} selenium args
      ext_args=None, # {dict} extension args
      executable_path=None, # {str} the hub's address
    ):

    merged_exp_args = self._get_exp_args(exp_args) 
    driver = StandardDriverCreator(
      std_args,
      merged_exp_args,
      cdp_args,
      sel_args,
      ext_args,
      executable_path,
    ).create()

    super().__init__(driver)
    
    # must refresh before to open a page or it will load the pc documet
    self.interactor.navi.refresh()
    
  def _get_exp_args(self,exp_args):
    args = {
      "mobileEmulation": {
        "deviceName": "iPhone 12 Pro"
      },
    }

    if not exp_args :
      return args     
    else:
      return {**args,**exp_args}
from .Browser import Browser
from .driver.HeadlessDriverCreator import HeadlessDriverCreator  

class BluesHeadlessChrome(Browser):

  def __init__(self,
      std_args=None, # {dict} standard args
      exp_args=None, # {dict} experimentalargs
      cdp_args=None, # {dict} chrome devtools protocal args
      sel_args=None, # {dict} selenium args
      ext_args=None, # {dict} extension args
      executable_path=None, # {str} driver.exe path: 'env' - using the env; 'xxx' - the local path; None - using the driver manager
    ):
    driver = HeadlessDriverCreator(
      std_args,
      exp_args,
      cdp_args,
      sel_args,
      ext_args,
      executable_path
    ).create()

    super().__init__(driver)
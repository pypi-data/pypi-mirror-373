from .BluesLoginChrome import BluesLoginChrome

class BluesHeadlessLoginChrome(BluesLoginChrome):

  def __init__(self,
      std_args=None, # {dict} standard args
      exp_args=None, # {dict} experimentalargs
      cdp_args=None, # {dict} chrome devtools protocal args
      sel_args=None, # {dict} selenium args
      ext_args=None, # {dict} extension args
      executable_path=None, # {str} driver.exe path: 'env' - using the env; 'xxx' - the local path; None - using the driver manager
      loginer_schema = None, # {Schema} : the atomed loginer schema
    ):

    args = {
      'headless':True,
      'imageless':True,
    }

    merged_std_args = {**std_args,**args} if std_args else args

    super().__init__(
      merged_std_args,
      exp_args,
      cdp_args,
      sel_args,
      ext_args,
      executable_path,
      loginer_schema
    )
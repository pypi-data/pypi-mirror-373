from .ChromeStdArgs import ChromeStdArgs   
from .ChromeExpArgs import ChromeExpArgs   
from .ChromeExtArgs import ChromeExtArgs   
from .ChromeCDPArgs import ChromeCDPArgs
from .ChromeSelArgs import ChromeSelArgs

class ChromeArgsFactory:
  
  def __init__(self,std_args=None,exp_args=None,cdp_args=None,sel_args=None,ext_args=None):
    self.__std_args = std_args if std_args else {}
    self.__exp_args = exp_args if exp_args else {}
    self.__cdp_args = cdp_args if cdp_args else {}
    self.__sel_args = sel_args if sel_args else {}
    self.__ext_args = ext_args if ext_args else {}

  def create(self):
    std_args = ChromeStdArgs(self.__std_args).get()
    exp_args = ChromeExpArgs(self.__exp_args).get()
    cdp_args = ChromeCDPArgs(self.__cdp_args).get()
    sel_args = ChromeSelArgs(self.__sel_args).get()
    ext_args = ChromeExtArgs(self.__ext_args).get()

    # connet to a exist browser, don't support experimental options setting 需要在Driver创建时设置，此种情况下仅连接 
    if sel_args.get('debugger_address'):
      std_args = None # has no effect
      exp_args = None # must remove

    return {
      'std':std_args,
      'exp':exp_args,
      'cdp':cdp_args,
      'sel':sel_args,
      'ext':ext_args,
    }

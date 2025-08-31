from .DriverCreator import DriverCreator

class HeadlessDriverCreator(DriverCreator):
  
  def __init__(self,
      std_args=None,
      exp_args=None,
      cdp_args=None,
      sel_args=None,
      ext_args=None,
      executable_path=None
    ):
    super().__init__(
      std_args,
      exp_args,
      cdp_args,
      sel_args,
      ext_args,
      executable_path
    )
    self.__set() 
    
  def __set(self):
    args = {
      'headless':True,
      'imageless':True,
    }
    self._std_args.update(args)
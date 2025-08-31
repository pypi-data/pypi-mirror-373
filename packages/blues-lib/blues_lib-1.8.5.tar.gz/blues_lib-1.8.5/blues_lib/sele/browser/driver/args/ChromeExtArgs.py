from .ChromeArgs import ChromeArgs

class ChromeExtArgs(ChromeArgs):

  __default_args = [
    # 加载 Chrome 扩展插件,在需要测试扩展功能或加载特定插件时使用。such as  '/path/to/extension.crx'
  ]
    
  def get(self):
    '''
    Get the default and input experimental args
    @returns {list} : removed duplicate args
    '''
    arg_list = self.__default_args+self.get_from_input()
    return list(set(arg_list))
  
  def get_from_input(self):
    '''
    Convert the pass standard args settings to the real args
      - replace the input value to the placehoder
    '''
    args = []
    if not self._input_args:
      return args
    
    for key,value in self._input_args.items():
      if value:
        args.append(key)
    return args

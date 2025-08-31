from .ChromeArgs import ChromeArgs

# Chrome DevTools Protocal 浏览器启动后动态设置,必须在get打开页面之前设置
class ChromeCDPArgs(ChromeArgs):

  __default_args = {
    'Network.setUserAgentOverride':{
      # 设置用户代理
      'userAgent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    },
    # 移除navigator上的webdriver标识
    'Page.addScriptToEvaluateOnNewDocument':{
      'source': "Object.defineProperty(navigator, 'webdriver', {get: () => undefined});"
    },
  }
    
  def get(self):
    '''
    Get the default and input experimental args
    @returns {dict} : removed duplicate args
    '''
    return {**self.__default_args,**self.get_from_input()}
  
  def get_from_input(self):
    '''
    Convert the pass standard args settings to the real args
      - replace the input value to the placehoder
    '''
    args = {}
    if not self._input_args:
      return args
    
    for key,value in self._input_args.items():
      args[key] = value # value maybe 0
    return args

from .ChromeArgs import ChromeArgs

class ChromeSelArgs(ChromeArgs):

  # selenium 配置项，非Chrome配置
  __default_args = {
    'page_load_strategy':'eager', # 控制页面加载策略，决定 Selenium 何时认为页面加载完成。normal：等待整个页面加载完成（默认）; eager：等待 DOM 加载完成，忽略图片等资源; none：不等待页面加载，立即返回。
    'unhandled_prompt_behavior':'dismiss', # 如何处理未处理的浏览器提示（如 alert、confirm 等）: accept：自动接受提示; dismiss：自动关闭提示。ignore：忽略提示。 }
    'accept_insecure_certs':True, # 是否接受不安全的 HTTPS 证书。
    'strict_file_interactability':True, # 控制文件上传/下载交互的严格模式。
  }
    
  # 默认不启用，需要调用端主动传入
  __optional_args = {
    'timeouts':None, # 设置 Selenium 的各种超时时间（如页面加载、脚本执行、元素查找等）。{"implicit": 5000, "pageLoad": 30000, "script": 10000}
    # 连接到已打开的 Chrome 浏览器实例。在调试或需要复用已有浏览器会话时使用。 IP地址:端口 such as 127.0.0.1:9222
    # 当你已经有一个 Chrome 浏览器实例在运行，并且你想通过 Selenium 连接到这个实例时，才需要设置 debuggerAddress。
    # debuggerAddress 本身并不启动 Chrome 浏览器，它只是告诉 Selenium 去连接一个已经存在的浏览器实例。
    # 这是一个特殊的selenium本身的属性，实际是作为属性添加的 options.debugger_address = "127.0.0.1:9222"
    'debugger_address':'',
    # 指定 Chrome 浏览器的可执行文件路径。在系统中有多个 Chrome 版本或需要指定特定版本时使用。 such as  r'C:\Program Files\Google\Chrome\Application\chrome.exe' 
    'binary_location':'', 
  }

  def get(self):
    '''
    Get the default and input experimental args
    @returns {list} : removed duplicate args
    '''
    args = {**self.__default_args,**self.get_from_input()}
    return args
  
  def get_from_input(self):
    args = {}
    if not self._input_args:
      return args

    # 直接使用入参 
    for key,value in self._input_args.items():
      args[key] = value
    return args

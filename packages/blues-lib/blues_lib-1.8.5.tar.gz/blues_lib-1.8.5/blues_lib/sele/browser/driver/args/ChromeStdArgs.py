from .ChromeArgs import ChromeArgs

class ChromeStdArgs(ChromeArgs):

  __default_args = [
    
    # 窗口设置
    '--start-maximized', # 启动浏览器时最大化窗口。在自动化测试中，最大化窗口可以确保页面元素完全可见，避免因分辨率问题导致的元素定位失败。
    
    # 安全设置
    '--ignore-ssl-errors', # 忽略 SSL 证书错误。在测试或爬虫中，访问使用自签名证书的网站时使用。
    '--ignore-certificate-errors', # 忽略证书错误。在测试或爬虫中，访问使用无效证书的网站时使用。
    '--disable-web-security', # 禁用同源策略（用于测试跨域请求）。
    '--allow-running-insecure-content', # 允许运行不安全的内容。
    
    # 工程设置
    '--enable-unsafe-swiftshader', # 启用 SwiftShader（一种软件渲染器）
    '--disable-webgl', # 禁用 WebGL，避免告警
    '--disable-webrtc', # 禁用 WebRTC，避免告警

    # 性能设置
    '--disable-extensions', # 禁用所有 Chrome 扩展程序。在测试中，避免扩展程序干扰浏览器行为。
    '--disable-extensions-api', # 禁用 Chrome 扩展程序的 API。在测试中，避免扩展程序干扰浏览器行为。
    '--disable-popup-blocking', # 禁用浏览器的弹出窗口阻止功能。在测试需要弹出窗口的功能时使用，如广告或登录窗口。
    '--disable-dev-shm-usage', # 禁用 /dev/shm 的使用（适用于 Docker 或内存受限环境）。

    # 自动化相关设置
    '--disable-blink-features=AutomationControlled', # 禁用自动化控制检测（避免被网站识别为自动化工具）。
    '--disable-infobars', # 隐藏 Chrome 顶部的“Chrome 正受到自动测试软件控制”提示栏。在自动化测试中，避免提示栏干扰页面布局或测试逻辑。
    '--enable-clipboard-features=AllowDirectSAP', # 支持剪切板复制 

    # 系统通知检查类设置
    '--disable-notifications', # 禁用浏览器的通知功能。在测试或爬虫中，避免网站弹出通知干扰操作。
    '--hide-crash-restore-bubble', # 隐藏浏览器崩溃后恢复页面的提示气泡。在自动化测试中，避免崩溃恢复提示干扰测试逻辑。
    '--disable-application-install-prompt', # 禁用应用安装提示。在测试中，避免网站提示安装应用干扰测试流程。
    '--no-first-run', # 跳过 Chrome 的首次运行向导。在自动化测试中，避免首次运行向导干扰测试流程。
    '--disable-first-run-ui', # 禁用首次运行时的用户界面（如欢迎页面）。在自动化测试中，避免首次运行界面干扰测试流程。
    '--no-default-browser-check', # 禁止 Chrome 检查是否设置为默认浏览器。在自动化测试中，避免浏览器弹出提示框干扰测试流程。
    '--disable-default-apps', # 禁用默认应用。
    '--disable-geolocation', # 禁用地理位置请求
    '--disable-save-password-bubble', # 禁用保存密码提示
    '--disable-translate', # 禁用翻译提示

    # 环境兼容设置 
    '--disable-gpu', # 禁用 GPU 加速，避免某些环境下的兼容性问题。在无头模式下运行时，某些系统可能会报错，禁用 GPU 可以规避这些问题。
    '--no-sandbox', # 禁用沙盒模式，避免某些环境下的权限问题。在 Linux 或 Docker 环境中运行时，沙盒模式可能会导致浏览器无法启动。
  ]

  # 默认不启用，根据入参确定是否启用
  __optional_args = {
    'headless':'--headless', # 启用无头模式，浏览器在后台运行，不显示可视化界面。适用于服务器环境或不需要可视化界面的自动化测试场景，如爬虫或持续集成（CI）环境。
    'incognito':'--incognito', # 启用隐身模式（无痕模式），浏览器不会保存历史记录、缓存和 Cookie。 在需要隔离会话的测试场景中，如测试登录功能或避免缓存干扰。
    'imageless':'blink-settings=imagesEnabled=false', # 禁用图片加载。在爬虫或测试中，禁用图片可以加快页面加载速度。完全禁用所有图片（包括 CSS 背景）
    # 语言
    'lang':'--lang=$()', # 系统语言 such as: zh-CN
    # 启用远程调试端口,Chrome 浏览器的启动参数，用于指定 Chrome 启动时监听的调试端口。 such as: 9222
    # 当你需要启动一个新的 Chrome 浏览器实例，并希望它启用远程调试功能时，才需要设置这个参数。
    'debugport':'--remote-debugging-port=$()', 
    # 指定 Chrome 监听调试连接的网络接口（IP 地址）。默认是本地 127.0.0.1 - 本地机器连接；0.0.0.0 允许任何设备通过 IP 地址和端口连接到 Chrome 的调试服务。
    'debugaddr':'--remote-debugging-address=$()',
    # 用户信息目录
    'debugdir':'--user-data-dir=$()',
    # 日志设置
    'logable':'--enable-logging', # 启用浏览器日志输出。
    'loglevel':'--v=$()', # 设置日志详细级别（1 为最低，9 为最高）such as: 1
  }

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
      arg = self.__optional_args.get(key)
      if not arg:
        continue

      arg = arg.replace('$()',str(value))
      args.append(arg)
    return args

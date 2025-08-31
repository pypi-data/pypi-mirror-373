import sys,os,re
from .ChromeArgs import ChromeArgs
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.file.File import File

class ChromeExpArgs(ChromeArgs):

  # 传入设置的目录分隔线必须与系统要求一致
  __download_dir = os.path.normpath(File.get_dir_path('browser_download'))
  __exclusion = [
    'enable-automation', # 隐藏“Chrome 正受到自动测试软件控制”提示栏。在自动化测试中，避免被网站检测到自动化工具。
  ] 
  __perfs = {
    # 通知设置
    "profile.default_content_settings.popups": 0,       # 禁止弹窗（防止某些站点拦截下载）
    'profile.default_content_setting_values.notification': 2, # 通知权限 0 - Default, 1 - Allow, 2 - Block
    'profile.default_content_setting_values.popups': 0, # 控制网页中通过 window.open() 或 <a target="_blank"> 触发的弹窗窗口  0 - Default, 1 - Allow, 2 - Block
    
    # 界面设置
    'autofill.profile_enabled':False, # 启用自动填充表单, False（禁用）
    
    # 下载配置
    'download.default_directory':__download_dir, # 下载目录, 默认 "C:\\Users\\Downloads"
    'download.prompt_for_download':False, # 是否提示下载路径, False（禁用提示，直接下载到默认目录）
    'download.directory_upgrade':True, # 自动升级下载目录权限
    'download.extensions_to_open':'', # 移除所有直接打开文件类型, such as: "pdf"（直接打开 PDF 文件，不下载）
    'safebrowsing.enabled':False, # 启用安全浏览（屏蔽危险文件）
    "safebrowsing.disable_download_protection": True,   # 允许下载"危险文件"（如 .exe）
    
    # 插件与扩展相关
    'plugins.plugins_disabled':[
      "Chrome PDF Viewer",       # 禁用内置 PDF 预览
      "Adobe Flash Player",      # 禁用 Flash
    ], # 禁用指定插件（需插件 ID）
    'plugins.always_open_pdf_externally':True, # PDF 直接下载（不预览）
    'profile.default_content_setting_values.plugins':1, # 插件全局权限,1（允许）或 2（阻止）
    
    # 资源加载
    'profile.default_content_setting_values.images':0, # 用户级别的图片加载控制,设置为 2 会阻止网页中的 <img> 图片加载, 不阻止 CSS 背景图（如 background-image）、Base64 内联图片、Canvas 绘制的图像。
    'profile.managed_default_content_settings.stylesheets': 0, # 阻止 CSS 加载
    'profile.managed_default_content_settings.javascript': 0, # 阻止 JavaScript 执行
    
  }

  __default_args = {
    'detach':True, # 保持浏览器窗口在脚本结束后不关闭。在调试或需要手动检查页面时使用。
    'excludeSwitches':__exclusion, # 排除项,禁用指定的功能项目
    'useAutomationExtension':False, # 禁用自动化扩展，避免被检测到自动化工具。在需要绕过反爬虫机制或自动化检测的场景中使用。
    'prefs':__perfs, # 设置浏览器的首选项（Preferences）用于配置浏览器的默认行为，如禁用图片、设置下载目录等。
  }
    
  def get(self):
    '''
    Get the default and input experimental args
    @returns {dict}
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

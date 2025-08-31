import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from command.NodeCommand import NodeCommand
from type.output.STDOut import STDOut
from sele.browser.BrowserFactory import BrowserFactory   
from namespace.CommandName import CommandName

class Creator(NodeCommand):

  NAME = CommandName.Browser.CREATOR
  TYPE = CommandName.Type.ACTION
  
  def _setup(self):
    super()._setup()
    self._mode =  self._node_conf.get('mode')
    self._exec_path = self._node_conf.get('path')

  def _invoke(self)->STDOut:
    browser = self._get_br()
    return STDOut(200,'ok',browser) if browser else STDOut(500,'failed to create the browser')

  def _get_br(self):
    if self._mode == 'proxy':
      return self._get_proxy_br()

    if self._mode == 'login':
      return self._get_login_br()

    return BrowserFactory(self._mode).create(executable_path=self._exec_path)
  
  def _get_login_br(self):
    browser = BrowserFactory(self._mode).create(executable_path=self._exec_path)
    kwargs = {
      'login_url':self._node_conf.get('login_url'),
      'logged_in_url':self._node_conf.get('logged_in_url'),
      'login_element':self._node_conf.get('login_element'),
      'wait_time':self._node_conf.get('wait_time'),
    }

    if not browser.login(**kwargs):
      raise Exception(f'[{self.NAME}] Failed to login')
    return browser

  def _get_proxy_br(self):
    kwargs = {
      'executable_path':self._exec_path,
      'proxy_config':self._node_conf.get('proxy'),
      'cookie_config':self._node_conf.get('cookie'),
    }
    return BrowserFactory(self._mode).create(**kwargs)

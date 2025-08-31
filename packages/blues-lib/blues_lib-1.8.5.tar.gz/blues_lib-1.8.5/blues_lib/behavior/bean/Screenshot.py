import sys,os,re
from typing import Any
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from behavior.bean.Bean import Bean

class Screenshot(Bean):

  def _get(self)->Any:
    if self._config.get('target_CS_WE'):
      kwargs = self._get_kwargs(['target_CS_WE','file','parent_CS_WE','timeout'])
      return self._browser.element.shot.screenshot(**kwargs)
    else:
      file = self._config.get('file','')
      return self._browser.interactor.window.screenshot(file)

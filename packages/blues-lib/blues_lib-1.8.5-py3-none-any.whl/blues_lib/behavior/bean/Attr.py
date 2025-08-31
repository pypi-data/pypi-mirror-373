import sys,os,re
from typing import Any
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from behavior.bean.Bean import Bean

class Attr(Bean):

  def _get(self)->Any:
    kwargs = self._get_kwargs(['target_CS_WE','key','parent_CS_WE','timeout'])
    return self._browser.element.info.get_attr(**kwargs)

  def _set(self):
    selector = self._config.get('target_CS_WE')
    key = self._config.get('key')
    value = self._config.get('value')
    if not key:
      return 

    attrs = {
      key:value
    }
    return self._browser.script.javascript.attr(selector,attrs)

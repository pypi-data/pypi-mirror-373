import sys,os,re
from typing import Any
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from behavior.bean.Bean import Bean

class CSS(Bean):

  def _get(self)->str:
    kwargs = self._get_kwargs(['target_CS_WE','key','parent_CS_WE','timeout'])
    return self._browser.element.info.get_css(**kwargs)
  
  def _set(self):
    selector = self._config.get('target_CS_WE')
    value = self._config.get('value')
    parent_selector = self._config.get('parent_CS_WE')
    return self._browser.script.javascript.css(selector,value,parent_selector)
import sys,os,re
from typing import Any
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from behavior.bean.Bean import Bean

class Choice(Bean):

  def _set(self)->Any:
    kwargs = self._get_kwargs(['target_CS_WE','parent_CS_WE','timeout'])
    is_select = self._config.get('value',True)
    if is_select:
      return self._browser.element.choice.select(**kwargs)
    else:
      return self._browser.element.choice.deselect(**kwargs)

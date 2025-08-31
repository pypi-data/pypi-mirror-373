import sys,os,re
from typing import Any
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from behavior.bean.Bean import Bean

class Select(Bean):

  def _set(self)->Any:
    kwargs = self._get_kwargs(['target_CS_WE','value','parent_CS_WE','timeout'])
    return self._browser.element.select.select_by_value_or_text(**kwargs)

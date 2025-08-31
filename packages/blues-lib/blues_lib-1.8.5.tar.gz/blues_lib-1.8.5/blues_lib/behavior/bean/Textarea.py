import sys,os,re
from typing import Any
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from behavior.bean.Bean import Bean

class Textarea(Bean):

  _get_keys = ['target_CS_WE','parent_CS_WE','timeout']
  _set_keys = ['target_CS_WE','value','LF_count','parent_CS_WE','timeout','input_by_para']

  def _get(self)->str:
    kwargs = self._get_kwargs(self._get_keys)
    return self._browser.element.info.get_text(**kwargs)

  def _set(self)->Any:
    kwargs = self._get_kwargs(self._set_keys)
    return self._browser.element.input.write_para(**kwargs)

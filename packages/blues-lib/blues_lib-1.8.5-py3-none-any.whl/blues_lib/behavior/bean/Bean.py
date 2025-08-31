import sys,os,re
from typing import Any
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.output.STDOut import STDOut
from type.executor.Behavior import Behavior

class Bean(Behavior):

  def execute(self)->STDOut:
    value = None
    try:
      if self._action()=='setter':
        value = self._set()
      else:
        value = self._get()
      return STDOut(200,'ok',value)
    except Exception as e:
      return STDOut(500,str(e),value)

  def _get(self)->Any:
    pass

  def _set(self)->Any:
    pass

  def _action(self)->str:
    action = 'getter'
    if 'value' in self._config:
      action = 'setter'
    return action
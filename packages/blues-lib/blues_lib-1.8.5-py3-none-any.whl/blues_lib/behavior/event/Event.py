import sys,os,re
from typing import Any
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.output.STDOut import STDOut
from type.executor.Behavior import Behavior

class Event(Behavior):

  def execute(self)->STDOut:
    value = None
    try:
      value = self._trigger()
      return STDOut(200,'ok',value)
    except Exception as e:
      return STDOut(500,str(e),value)

  def _trigger(self)->Any:
    pass
import sys,os,re
from typing import Any
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from util.BluesDateTime import BluesDateTime
from behavior.general.General import General

class Wait(General):

  def _do(self)->Any:
    kwargs = self._get_kwargs(['duration','title'])
    return BluesDateTime.count_down(kwargs)
import sys,os,re
from typing import Any
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from behavior.event.Event import Event

class Frameout(Event):

  def _trigger(self)->Any:
    return self._browser.interactor.frame.switch_to_default()
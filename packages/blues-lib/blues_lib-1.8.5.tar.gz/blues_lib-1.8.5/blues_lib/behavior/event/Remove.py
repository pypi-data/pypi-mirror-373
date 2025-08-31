import sys,os,re
from typing import Any
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from behavior.event.Event import Event

class Remove(Event):

  def _trigger(self)->Any:
    kwargs = self._get_kwargs(['target_CS_WE'])
    return self._browser.element.popup.remove(**kwargs)
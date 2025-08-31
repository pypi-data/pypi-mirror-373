import sys,os,re
from typing import Any
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from behavior.event.Event import Event

class Open(Event):

  def _trigger(self)->Any:
    url = self._config.get('url')
    try:
      self._browser.open(url)
      return True
    except Exception as e:
      return False

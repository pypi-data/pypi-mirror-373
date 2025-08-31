import sys,os,re,time
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from behavior.event.Event import Event
from util.AutoGUI import AutoGUI

class Keyboard(Event):

  def _trigger(self)->bool:
    key:str = self._config.get('key','')
    if not key:
      return False

    AutoGUI.press(key)
    return True


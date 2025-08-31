import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from behavior.checker.Checker import Checker

class ElePresents(Checker):

  def _check(self)->bool:
    '''
    check if the element is present in the page
    @returns {bool}
    '''
    target_CS_WE:str = self._config.get('target_CS_WE')
    wait_time:int = self._config.get('wait_time',3)
    return bool(self._browser.waiter.ec.to_be_presence(target_CS_WE,wait_time))

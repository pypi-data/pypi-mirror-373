import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from behavior.checker.Checker import Checker

class UrlChanges(Checker):

  def _check(self)->bool:
    '''
    if the url changes in the wait time, it will ignore the query params and fragments
    @returns {bool}
    '''
    url = self._config.get('url')
    wait_time = self._config.get('wait_time',3)
    return self._browser.waiter.ec.url_changes(url,wait_time)

import sys,os,re
from typing import List
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from behavior.bean.Bean import Bean

class BrCookie(Bean):

  def _get(self)->List[dict]:
    # read cookie from the browser
    return self._browser.interactor.cookie.get()

  def _set(self)->bool:
    # get cookie from the local file and set to the browser
    cookies = self._config['value']
    if not cookies or cookies == '__sentinel__':
      cookies = self._browser.read_cookies()
 
    if not cookies:
      self._logger.warning(f'[{self.__class__.__name__}] Failed to read cookies from the local file')
      return False

    self._logger.info(f'[{self.__class__.__name__}] Managed to set cookies to the browser')
    self._browser.interactor.cookie.replace(cookies)
    return True

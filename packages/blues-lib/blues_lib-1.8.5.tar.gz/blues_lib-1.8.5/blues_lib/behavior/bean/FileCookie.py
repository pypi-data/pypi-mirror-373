import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from behavior.bean.Bean import Bean
from util.BluesDateTime import BluesDateTime

class FileCookie(Bean):
  '''
  This class is used to manage the local cookie file.
  '''

  def _get(self)->str:
    # read cookies from the local file
    return self._browser.read_cookies()

  def _set(self)->str:
    '''
    save cookies to the local file
    @returns : the local file path
    '''
    wait_time = self._config.get('wait_time',5)
    BluesDateTime.count_down({
      'duration':wait_time,
      'title':f'Wait for {wait_time} seconds to capture the cookies...'
    })
    local_file = self._config['value']
    if not local_file or local_file == '__sentinel__':
      return self._browser.save_cookies()
    else:
      return self._browser.save_cookies(local_file)

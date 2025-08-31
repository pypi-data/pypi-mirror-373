import sys,os,re,time
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from behavior.bean.Bean import Bean
from util.Clipboard import Clipboard

class Copy(Bean):

  def _get(self)->str:
    # clear the clipboard before copy
    Clipboard.clear()
    
    # trigger the copy action
    kwargs = self._get_kwargs(['target_CS_WE','parent_CS_WE','timeout'])
    self._browser.action.mouse.click(**kwargs)
    time.sleep(0.5)
    
    # get the text from the clipboard
    return Clipboard.paste()

import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from behavior.bean.Bean import Bean

class Url(Bean):

  def _get(self)->str:
    return self._browser.interactor.document.get_url()

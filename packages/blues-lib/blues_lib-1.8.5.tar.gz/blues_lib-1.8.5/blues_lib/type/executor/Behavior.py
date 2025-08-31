from typing import List
import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.executor.Executor import Executor
from type.model.Model import Model
from sele.browser.Browser import Browser

class Behavior(Executor):
  def __init__(self,model:Model,browser:Browser=None)->None:
    super().__init__()
    self._meta = model.meta
    self._bizdata = model.bizdata
    self._config = model.config
    self._browser = browser

  def _get_kwargs(self,keys:List[str],config=None)->dict:
    '''
    Extract specified keys from configuration dictionary
    @param {List[str]} keys: list of keys to extract from config
    @param {dict} config: optional config dict to merge with self._config (config takes precedence)
    @return {dict}: dictionary containing only the specified keys and their values
    '''
    conf = {**self._config,**config} if config else self._config
    # must remove the attr that value is None
    key_conf = {}
    for key in keys:
      if key in conf:
        key_conf[key] = conf.get(key)
    return key_conf

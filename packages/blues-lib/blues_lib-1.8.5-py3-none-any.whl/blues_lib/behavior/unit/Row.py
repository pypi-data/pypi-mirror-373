import sys,os,re
from typing import Union,List,Any
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.executor.Behavior import Behavior
from type.output.STDOut import STDOut
from type.model.Model import Model
from sele.browser.Browser import Browser
from behavior.BhvExecutor import BhvExecutor
from behavior.unit.ConfigModifier import ConfigModifier

class Row(Behavior):
  
  def __init__(self,model:Model,browser:Browser=None):
    super().__init__(model,browser)
    self._chidlren:Union[dict,list] = self._config.get('children')

  def execute(self)->STDOut:
    try:
      rows = []
      parents = self._get_parents()
      for parent in parents:
        value = self._execute_unit(parent)
        if not value:
          continue
        rows.append(value)
      return STDOut(200,'ok',rows if rows else None)
    except Exception as e:
      return STDOut(500,str(e),None)
    
  def _get_parents(self)->List[Any]:
    target_CS_WE = self._config.get('target_CS_WE')
    parents = self._browser.waiter.querier.query_all(target_CS_WE)
    # the len>0
    return parents if parents else [None]

  def _execute_unit(self,parent=None)->Any:
    model = self._get_model(parent)
    executor = BhvExecutor(model,self._browser)
    stdout = executor.execute()
    return stdout.data
  
  def _get_model(self,parent):
    config_modifier = ConfigModifier(self._chidlren,parent)
    config = config_modifier.get_unit_config()
    return Model(config)

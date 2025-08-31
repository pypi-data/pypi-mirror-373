from typing import Dict,Any,Union
import copy

class ConfigModifier:

  def __init__(self,chidlren:Union[dict,list],parent:Any):
    self._children = chidlren
    self._parent = parent

  def get_unit_config(self)->Dict[str,dict]:
    if not self._parent or not self._children:
      return self._children
    
    if isinstance(self._children,dict):
      return self._get_map_config()

    if isinstance(self._children,list):
      return self._get_array_config()
    
    return self._children

  def _get_map_config(self)->dict:
    children_copy = {}

    for key,config in self._children.items():
      bhv_confg = self._get_bhv_config(config)
      children_copy[key] = bhv_confg
    
    return children_copy

  def _get_array_config(self)->list:
    children_copy = []

    for config in self._children:
      bhv_confg = self._get_bhv_config(config)
      children_copy.append(bhv_confg)
    
    return children_copy

  def _get_bhv_config(self,bhv_config:dict)->dict:
    conf = copy.copy(bhv_config)
    if conf.get('target_CS_WE'):
      conf['parent_CS_WE'] = self._parent
    else:
      conf['target_CS_WE'] = self._parent
    return conf



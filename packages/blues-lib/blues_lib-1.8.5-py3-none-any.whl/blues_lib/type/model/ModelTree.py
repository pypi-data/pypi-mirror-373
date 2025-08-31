import sys,os,re
from typing import Any
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.model.Model import Model

class ModelTree:
  @classmethod
  def create(cls, tree: Any, alt_bizdata:dict = None):
    '''
    convert model tree to model object
    :param tree: model tree
    :param alt_bizdata: business data, as the alternative data source
    :return: model object
    '''
    return cls._process(tree,alt_bizdata)

  @classmethod
  def _process_dict(cls, data: dict, alt_bizdata:dict = None):
    """Process dictionary data"""
    result = {}
    for key, value in data.items():
      result[key] = cls._process(value,alt_bizdata)  # Recursively process values through _process
    return result

  @classmethod
  def _process_list(cls, data: list, alt_bizdata:dict = None):
    """Process list data"""
    return [cls._process(item,alt_bizdata) for item in data]  # Recursively process items through _process

  @classmethod
  def _process(cls, value:Any, alt_bizdata:dict = None):

    """Central processing method that handles all value types"""
    # Check for __model__ pattern first (highest priority)
    if isinstance(value, list) and len(value) >= 2 and value[0] == '__model__':
      meta = value[1]
      # 1. 优先检查 value[2] 是否存在且为非空值
      if len(value) > 2 and value[2]:
        bizdata = value[2]
      # 2. 若 value[2] 不符合，则检查 alt_bizdata 是否为非空值
      elif alt_bizdata:
        bizdata = alt_bizdata
      # 3. 若前两者都为空值，则使用空字典兜底
      else:
        bizdata = {}
      return Model(meta, bizdata)
    
    # Handle dict processing
    elif isinstance(value, dict):
      return cls._process_dict(value,alt_bizdata)
    
    # Handle list processing
    elif isinstance(value, list):
      return cls._process_list(value,alt_bizdata)
    
    # Return all other types as-is
    else:
      return value
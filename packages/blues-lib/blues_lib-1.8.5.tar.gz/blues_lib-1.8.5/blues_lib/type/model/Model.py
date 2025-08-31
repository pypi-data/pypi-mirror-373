import sys,os,re
from typing import Union
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from util.BluesDateTime import BluesDateTime

class Model:
  def __init__(self, meta: Union[dict, list], bizdata: dict = None) -> None:
    self.meta = meta
    self.bizdata = self._replace_func(bizdata)
    self.config = self.interpolate(self.meta, self.bizdata)
    
  def refresh(self):
    # the meta or bizdata may be updated by the user
    self.config = self.interpolate(self.meta, self.bizdata)

  def interpolate(self, meta: Union[dict, list], bizdata: dict) -> Union[dict, list]:
    """
    递归替换meta中的占位符(${key})为bizdata中对应的值，不修改原对象
    
    Args:
      meta: 包含占位符的字典或列表
      bizdata: 用于替换占位符的数据字典
    
    Returns:
      替换后的新结构
    """
    if not bizdata:
      return meta

    if isinstance(meta, dict):
      return self._process_dict(meta, bizdata)
    elif isinstance(meta, list):
      return self._process_list(meta, bizdata)
    else:
      return meta  # 非容器类型直接返回
    
  def _replace_func(self,bizdata)->dict:
    '''
    Replace the func placeholders in the bizdata
    '''
    replaced_bizdata = {}
    if not bizdata:
      return bizdata
    
    for key,value in bizdata.items():
      if not value or not isinstance(value, str):
        replaced_bizdata[key] = value
        continue 

      full_match = re.fullmatch(r'\$\{([^}]+)\}', value)
      if full_match:
        func = full_match.group(1)
        if func == 'timestamp':
          replaced_bizdata[key] = BluesDateTime.get_timestamp()
          continue 
      
      replaced_bizdata[key] = value
    
    return replaced_bizdata

  def _process_dict(self, obj: dict, data: dict) -> dict:
    """递归处理字典，创建新对象"""
    result = {}
    for key, value in obj.items():
      if isinstance(value, dict):
        result[key] = self._process_dict(value, data)
      elif isinstance(value, list):
        result[key] = self._process_list(value, data)
      elif isinstance(value, str):
        result[key] = self._replace_placeholders(value, data)
      else:
        result[key] = value  # 非字符串类型保持原样
    return result

  def _process_list(self, arr: list, data: dict) -> list:
    """递归处理列表，创建新对象"""
    result = []
    for item in arr:
      if isinstance(item, dict):
        result.append(self._process_dict(item, data))
      elif isinstance(item, list):
        result.append(self._process_list(item, data))
      elif isinstance(item, str):
        result.append(self._replace_placeholders(item, data))
      else:
        result.append(item)  # 非字符串类型保持原样
    return result

  def _replace_placeholders(self, s: str, data: dict) -> Union[str, int, float, bool, list, dict, None]:
    """替换字符串中的占位符，保留原始类型"""
    if not isinstance(s, str):
      return s
      
    # 检查整个字符串是否就是一个占位符
    full_match = re.fullmatch(r'\$\{([^}]+)\}', s)
    if full_match:
      expr = full_match.group(1)
      
      # 处理带默认值的情况: ${key:default}
      if ':' in expr:
        key, default_str = expr.split(':', 1)
        value = data.get(key, default_str)
        # 尝试将默认值转换为原始类型
        if isinstance(value, str):
          return self._convert_to_original_type(value)
        return value
      
      # 处理简单占位符
      value = data.get(expr, s)
      return value
    
    # 处理包含多个占位符或其他文本的字符串
    def replace_match(match):
      expr = match.group(1)
      
      # 处理带默认值的情况: ${key:default}
      if ':' in expr:
        key, default = expr.split(':', 1)
        return str(data.get(key, default))
      
      # 处理简单占位符
      return str(data.get(expr, match.group(0)))
    
    return re.sub(r'\$\{([^}]+)\}', replace_match, s)

  def _convert_to_original_type(self, value_str: str) -> Union[str, int, float, bool, list, dict, None]:
    """尝试将字符串转换为原始类型"""
    # 处理布尔值
    if value_str.lower() == 'true':
      return True
    if value_str.lower() == 'false':
      return False
    
    # 处理None
    if value_str.lower() == 'none':
      return None
    
    # 处理数字
    try:
      num = int(value_str)
      return num
    except ValueError:
      try:
        num = float(value_str)
        return num
      except ValueError:
        pass
    
    # 处理列表和字典（如果需要更复杂的解析，可以使用ast.literal_eval）
    if value_str.startswith('[') and value_str.endswith(']'):
      # 简单列表解析，不处理嵌套结构
      items = [item.strip() for item in value_str[1:-1].split(',')]
      return items
    
    if value_str.startswith('{') and value_str.endswith('}'):
      # 简单字典解析，不处理嵌套结构
      pairs = [pair.strip() for pair in value_str[1:-1].split(',')]
      result = {}
      for pair in pairs:
        if ':' in pair:
          key, val = pair.split(':', 1)
          result[key.strip()] = val.strip()
      return result
    
    # 默认返回字符串
    return value_str
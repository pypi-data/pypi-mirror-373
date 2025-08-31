from typing import Any

class NestedDataUpdater:
  """嵌套数据写入器，通过路径字符串合并数据"""
  
  @staticmethod
  def update(data,value):
    if not data or not value:
      return 
    if isinstance(data,list) and isinstance(value,list):
      data.extend(value)
    elif isinstance(data,dict) and isinstance(value,dict):
      data.update(value)

  @staticmethod
  def write_by_path(data: Any, path: str, value: Any) -> bool:
    """
    通过路径写入数据，类型不匹配时返回False（不写入）
    
    参数:
        data: 原始数据（可以是字典、列表或其他可嵌套的数据结构）
        path: 目标路径字符串，支持字典属性和列表下标，例如 'summary.query'、'0.summary.query.1.answer'
        value: 要写入的值
    
    返回:
        是否成功写入
    """
    if not path:
      NestedDataUpdater.update(data,value)
      return True  # if hava no path, assign the value to the root data
    
    parts = path.split('.')
    parent_parts = parts[:-1]
    last_part = parts[-1]
    
    # 找到父节点
    current: Any = data
    for part in parent_parts:
      if isinstance(current, list):
        try:
          index = int(part)
          if 0 <= index < len(current):
            current = current[index]
          else:
            return False
        except ValueError:
          return False
      elif isinstance(current, dict):
        if part in current:
          current = current[part]
        else:
          return False
      else:
        return False  # 中间节点不是可访问类型
    
    # 写入最后一个节点
    if isinstance(current, dict):
      # 字典允许任何字符串键
      NestedDataUpdater.update(current[last_part],value)
      return True
    elif isinstance(current, list):
      try:
        index = int(last_part)
        if 0 <= index < len(current):
          NestedDataUpdater.update(current[index],value)
          return True
        else:
          return False  # 列表索引越界
      except ValueError:
        return False  # 列表索引必须是整数
    else:
      return False  # 父节点不是字典或列表，无法写入
from typing import Any

class NestedDataReader:
  
  @staticmethod
  def read_by_path(data: Any, path: str) -> Any:
    """
    根据路径字符串获取数据中对应节点的值
    
    参数:
        data: 原始数据（可以是字典、列表或其他可嵌套的数据结构）
        path: 路径字符串，支持字典属性和列表下标，例如 'summary.query'、'0.summary.query.1.answer'
    
    返回:
        路径对应的节点值，如果路径不存在则返回 None
    """
    if not path:  # 空路径返回原始数据
      return data
    
    # 拆分路径为各个部分
    parts = path.split('.')
    current: Any = data
    
    for part in parts:
      # 处理列表类型
      if isinstance(current, list):
        try:
          # 尝试将路径部分转换为整数下标
          index = int(part)
          # 检查下标是否有效
          if 0 <= index < len(current):
            current = current[index]
          else:
            return None  # 下标越界
        except ValueError:
          return None  # 无法转换为整数，路径无效
      # 处理字典类型
      elif isinstance(current, dict):
        if part in current:
          current = current[part]
        else:
          return None  # 字典中不存在该键
      # 既不是列表也不是字典，无法继续访问
      else:
        return None
    
    return current
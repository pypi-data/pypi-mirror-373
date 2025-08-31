import sys,os,re
from typing import Dict, Any, Optional, List
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from util.BluesFiler import BluesFiler

class Querier:
  '''
  @description : support json json5 yaml hocon files query from the dir
  '''

  def __init__(self,base_dir:str='') -> None:
    self._base_dir = base_dir
  
  def get(self,*paths: str) -> Optional[Dict[str, Any]]:
    """根据路径参数生成模式字典
    
    Args:
        *paths: 目录路径链，例如('module', 'submodule')对应 module/submodule
        
    Returns:
        包含指定路径结构的字典，路径不存在时返回None
    """
    base_dir = self._get_base_dir()
    
    # 无参数时返回完整结构
    if not paths:
      return self._process_base_directory(base_dir)
    
    # 根据路径参数定位目标目录
    target_dir = self._find_target_directory(base_dir, paths)
    if not target_dir:
      return None
    
    # 构建目标目录的结构
    return self._build_schema(target_dir)

  
  def _find_target_directory(self,base_dir: str, paths: List[str]) -> Optional[str]:
    """递归查找目标目录
    
    Args:
        base_dir: 起始目录
        paths: 目录路径链
        
    Returns:
        目标目录的绝对路径，不存在时返回None
    """
    current_dir = base_dir
    for dir_name in paths:
      next_dir = os.path.join(current_dir, dir_name)
      if not self._is_valid_directory(dir_name, next_dir):
        return None
      current_dir = next_dir
    return current_dir

  
  def _get_base_dir(self) -> str:
    """获取基准目录路径（当前文件所在目录）"""
    return os.path.dirname(os.path.abspath(__file__)) if not self._base_dir else self._base_dir

  
  def _is_valid_directory(self,name: str, path: str) -> bool:
    """验证是否为有效目录（过滤Python特殊目录）"""
    return os.path.isdir(path) and not name.startswith('__')

  
  def _process_base_directory(self,base_dir: str) -> Dict[str, Any]:
    """处理基准目录下的所有条目"""
    final_schema: Dict[str, Any] = {}
    for item in os.listdir(base_dir):
      item_path = os.path.join(base_dir, item)
      if self._is_valid_directory(item, item_path):
        dir_schema = self._build_schema(item_path)
        if dir_schema:
          final_schema[item] = dir_schema
    return final_schema

  
  def _build_schema(self,current_path: str) -> Optional[Dict[str, Any]]:
    """递归构建目录结构字典"""
    schema: Dict[str, Any] = {}
    for entry in os.listdir(current_path):
      entry_path = os.path.join(current_path, entry)
      if os.path.isdir(entry_path):
        self._process_subdirectory(schema, entry, entry_path)
      else:
        self._process_file(schema, entry, entry_path)
    return schema if schema else None

  
  def _process_subdirectory(self,schema: Dict[str, Any], name: str, path: str) -> None:
    """处理子目录并更新到当前schema"""
    sub_schema = self._build_schema(path)
    if sub_schema:
      schema[name] = sub_schema

  
  def _process_file(self,schema: Dict[str, Any], filename: str, filepath: str) -> None:
    data = None
    if filename.endswith(('.yaml', '.yml')):
      data = BluesFiler.read_yaml(filepath)
    elif filename.endswith('.json5'):
      data = BluesFiler.read_json5(filepath)
    elif filename.endswith('.json'):
      data = BluesFiler.read_json(filepath)
    elif filename.endswith('.conf'):
      data = BluesFiler.read_hocon(filepath)
    
    if data:
      key_name = os.path.splitext(filename)[0]
      schema[key_name] = data

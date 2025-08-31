from typing import Any
import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))

from util.NestedDataReader import NestedDataReader
from util.NestedDataWriter import NestedDataWriter
from util.NestedDataUpdater import NestedDataUpdater

class NestedDataMapping:
  """嵌套数据映射类，用于在源数据和目标数据之间进行基于路径的映射"""
  @staticmethod
  def map(source_data: Any, source_path: str, target_data: Any, target_path: str, map_method='assign') -> bool:
    """
    将源数据中指定路径的值映射到目标数据的指定路径
    参数: 源数据、源路径、目标数据、目标路径
    返回: 映射是否成功
    """
    # 从源数据读取值
    value = NestedDataReader.read_by_path(source_data,source_path)
    if value is None:
        return False  # 源路径不存在或无法读取
    
    # 写入目标数据
    if map_method == 'update':
      return NestedDataUpdater.write_by_path(target_data,target_path,value)
    else:
      return NestedDataWriter.write_by_path(target_data,target_path,value)

import sys,os,re
import json
from typing import List,Dict,Any
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.output.SQLSTDOut import SQLSTDOut
from dao.sql.BluesSQLIO import BluesSQLIO    

class TableQuerier():

  def __init__(self,table:str,should_decode:bool=True)->None:
    self._table = table
    self._should_decode = should_decode
    self._io = BluesSQLIO()
  
  def get(self,fields:List[str]=None,conditions:List[dict]=None,orders:List[dict]=None,pagination:dict=None)->SQLSTDOut:
    '''
    Query rows
    Parameter:
      fields {list<str>} : the table fields 
      conditions {dict | list<dict>} : the standard condition value ,like:
        {'operator':'and','field':'material_id','comparator':'=','value':'id2'} 
        [{'operator':'and','field':'material_id','comparator':'=','value':'id2'}]
      orders {dict | list<dict>} : the standard order by dict, like:
        {'field':'material_status','sort':'asc'}
        [{'field':'material_status','sort':'asc'}]
      pagination {dict} : the standard pager dict, like:
        {'no':1,'size':10}
    Return:
      {SQLSTDOut} : the standard sql output,like:
    '''
    stdout = self._io.get(self._table,fields,conditions,orders,pagination)
    return self._decode_entities(stdout)
  
  def _decode_entities(self,stdout:SQLSTDOut):
    if stdout.code != 200 or not stdout.data or not self._should_decode:
      return stdout

    for entity in stdout.data:
      self._decode(entity)

    return stdout

  def first(self,conditions:List[dict]=None)->SQLSTDOut:
    stdout = self.get(conditions=conditions)
    if stdout.code != 200 or not stdout.data:
      return stdout
    
    return SQLSTDOut(200,'ok',stdout.data[0])

  @classmethod 
  def _decode(cls,entity: Dict[str, Any]) -> None:
    """
    Decodes JSON string fields in a dictionary to Python objects.
    
    This method modifies the input dictionary in-place, converting 
    JSON-formatted string values into their corresponding Python objects.
    Empty or whitespace-only strings are skipped to avoid invalid parsing.
    
    Args:
      entity: A dictionary representing a database row, 
        where keys are field names and values are field values.
    """
    for key, value in entity.items():
      if isinstance(value, str) and value.strip():  
        try:
          entity[key] = json.loads(value)
        except Exception as e:
          continue
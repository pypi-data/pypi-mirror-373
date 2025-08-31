import sys,os,re,json
from typing import List,Dict,Any,Union

sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.output.SQLSTDOut import SQLSTDOut
from dao.sql.BluesSQLIO import BluesSQLIO

class TableMutator():

  def __init__(self,table:str,should_encode:bool=True)->None:
    self._table = table
    self._should_encode = should_encode
    self._io = BluesSQLIO()
  
  def post(self,fields:List[str],values:List[List[Any]])->SQLSTDOut:
    '''
    Insert one more multi rows
    Parameter:
      fields {list<str>} : the table fields 
      values {list<list<str>>} : two-dim list, every list is a row field value
        the fields' length must be equal to the values row list's length
    Return:
      {dict} : the standard sql output,like:
         {'code': 200, 'count': 1, 'sql': 'insert xxx'}
    '''
    self._encode_entities(values)
    return self._io.post(self._table,fields,values)
  
  def insert(self,entities:List[dict])->SQLSTDOut:
    '''
    Insert one more multi rows
    Parameter:
      entities {dict | list<dict>} : every dict contains field:value
    Return:
      {dict} : the standard sql output,like:
         {'code': 200, 'count': 1, 'sql': 'insert xxx'}
    '''
    self._encode_entities(entities)
    return self._io.insert(self._table,entities)

  def put(self,fields:List[str],values:List[any],conditions)->SQLSTDOut:
    '''
    Update one or multi rows
    Parameter:
      fields {list<str>} : the table fields 
      values {list<any>} : the updated value
        the value's list length should be equal to the field's list length
      conditions {dict | list<dict>} : the standard condition value ,like:
        {'field':'material_id','comparator':'=','value':'id2'} 
        [{'field':'material_id','comparator':'=','value':'id2'}]
    Return:
      {dict} : the standard sql output,like:
         {'code': 200, 'count': 1, 'sql': 'update xxx'}
    '''
    self._encode_entity(values)
    return self._io.put(self._table,fields,values,conditions)

  def update(self,entity:dict,conditions:List[dict])->SQLSTDOut:
    '''
    Update one or multi rows
    Parameter:
      entity {dict} : every dict contains field:value
      conditions {dict | list<dict>} : the standard condition value ,like:
        {'field':'material_id','comparator':'=','value':'id2'} 
        [{'field':'material_id','comparator':'=','value':'id2'}]
    Return:
      {dict} : the standard sql output,like:
         {'code': 200, 'count': 1, 'sql': 'update xxx'}
    '''
    self._encode_entity(entity)
    return self._io.update(self._table,entity,conditions)

  def delete(self,conditions:List[dict])->SQLSTDOut:
    '''
    Delete one or multi rows
    Parameter:
      conditions {dict | list<dict>} : the standard condition value ,like:
        {'field':'material_id','comparator':'=','value':'id2'} 
        [{'field':'material_id','comparator':'=','value':'id2'}]
    Return:
      {dict} : the standard sql output,like:
         {'code': 200, 'count': 1, 'sql': 'delete xxx'}
    '''
    return self._io.delete(self._table,conditions)
  
  def _encode_entities(self,entities:List[any])->None:
    if self._should_encode and isinstance(entities,list):
      for entity in entities:
        self._encode_entity(entity)

  def _encode_entity(self,entity:Union[Dict[str, Any], List[Any]]) -> None:
    if self._should_encode:
      self._encode(entity)

  def _encode(self, entity: Union[Dict[str, Any], List[Any]]) -> None:
    """
    Encodes non-MySQL-native types in a dictionary or list to JSON strings (single level).
    Ignores inputs that are not dictionaries or lists.
    
    Args:
        entity: A dictionary or list representing data to be written to the database.
    
    Returns:
        The encoded entity (modified in-place for dictionaries, new list for lists),
        or the original input if it's not a dictionary or list.
    """
    mysql_types = {int, float, str, bool, type(None)}
    
    if isinstance(entity, dict):
      for key, value in entity.items():
        if type(value) in mysql_types:
          continue

        try:
          entity[key] = json.dumps(value, ensure_ascii=False)
        except json.JSONDecodeError as e:
          entity[key] = str(e)

    if isinstance(entity, list):
      for index,item in enumerate(entity):
        if type(item) in mysql_types:
          continue

        try:
          entity[index] = json.dumps(item, ensure_ascii=False)
        except json.JSONDecodeError as e:
          entity[index] = str(e)

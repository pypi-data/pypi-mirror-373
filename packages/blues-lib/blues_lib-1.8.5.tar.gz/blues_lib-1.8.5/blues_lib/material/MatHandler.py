import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.chain.AllMatchHandler import AllMatchHandler
from type.output.STDOut import STDOut
from dao.material.MatMutator import MatMutator 

class MatHandler(AllMatchHandler):
  
  def _setup(self):
    self._entities:list[dict] = self._request.get('entities')
    if not self._entities:
      message = f'[{self.__class__.__name__}] Received an empty entity'
      raise Exception(message)

    self._config:dict = self._request.get('config')
    if not self._config:
      message = f'[{self.__class__.__name__}] Received an empty config'
      raise Exception(message)

  def _log(self,stdout:STDOut):
    if stdout.code==200:
      message = f'[{self.__class__.__name__}] Managed to retain {len(stdout.data)} entities'
      self._logger.info(message)
    else:
      message = f'[{self.__class__.__name__}] Failed to retain any valid entities - {stdout.message}'
      self._logger.error(message)

  def _mark(self,entity:dict)->STDOut:
    '''
    Mark the invalid entity in the DB, avoid to duplicately crawl
    '''
    entity['mat_stat'] = "invalid"
    mat_entity = self._get_mat_entity(entity)
    return MatMutator().insert([mat_entity])
  
  def _get_mat_entity(self,entity:dict)->dict:
    # remove the unnecessary fields
    mat_entity:dict = {}
    for key in entity.keys():
      if self._is_mat_field(key):
        mat_entity[key] = entity[key]
    return mat_entity
  
  def _is_mat_field(self,field:str)->bool:
    return field.startswith('mat_')



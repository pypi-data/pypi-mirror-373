import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from material.MatHandler import MatHandler
from type.output.STDOut import STDOut
from dao.material.MatMutator import MatMutator 

class Sinker(MatHandler):

  def resolve(self)->STDOut:
    self._setup()
    config = self._config.get('sinker')
    if not config:
      return STDOut(200,'skip this sinker')

    self._method = config.get('method','insert')
    conditions:list[dict] = config.get('conditions')
    
    sink_entities:list[dict] = self._get_sink_entities(config)
    
    # insert to the db
    if self._method == 'insert':
      return MatMutator().insert(sink_entities)
    elif self._method == 'update':
      # only update the first entity
      return MatMutator().update(sink_entities[0],conditions)
    elif self._method == 'delete':
      return MatMutator().delete(conditions)
    else:
      self._logger.warning(f'[{self.__class__.__name__}] Skip to upsert - {self._method} is not supported')
      return STDOut(200,f'no support method: {self._method}')
    
  def _get_sink_entities(self,config:dict)->list[dict]:

    extend_entity:dict = config.get('entity') # the merged fields
    inc_fields:list[str] = config.get('inc_fields',[])
    inc_pattern:str = config.get('inc_pattern','')
    exc_fields:list[str] = config.get('dec_fields',[])
    exc_pattern:str = config.get('dec_pattern','')

    sink_entities:list[dict] = []
    
    for entity in self._entities:
      sink_entity:dict = entity.copy()
      # merge the entity
      if extend_entity:
        sink_entity.update(extend_entity)
        
      # include and exclude the fields
      if inc_fields:
        sink_entity = {k:v for k,v in sink_entity.items() if k in inc_fields}

      if inc_pattern:
        sink_entity = {k:v for k,v in sink_entity.items() if re.match(inc_pattern,k)}

      if exc_fields:
        sink_entity = {k:v for k,v in sink_entity.items() if k not in exc_fields}

      if exc_pattern:
        sink_entity = {k:v for k,v in sink_entity.items() if not re.match(exc_pattern,k)}

      sink_entities.append(sink_entity)
    return sink_entities
    


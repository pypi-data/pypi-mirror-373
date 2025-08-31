import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from material.MatHandler import MatHandler
from type.output.STDOut import STDOut
from dao.material.MatQuerier import MatQuerier

class Deduplicator(MatHandler):

  def resolve(self):
    self._setup()
    avail_entities = []
    querier = MatQuerier()

    for entity in self._entities:
      if querier.exist(entity['mat_id']):
        self._logger.warning(f'[{self.__class__.__name__}] Skip a existing entity - {entity["mat_title"]}')
      else:
        avail_entities.append(entity)

    self._request['entities'] = avail_entities
    stdout = STDOut(200,'ok',avail_entities) if avail_entities else STDOut(500,'all are duplicated')
    self._log(stdout)
    return stdout
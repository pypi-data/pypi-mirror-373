import sys,os,re
from typing import List
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.output.STDOut import STDOut
from util.BluesAlgorithm import BluesAlgorithm 
from util.BluesURL import BluesURL
from material.MatHandler import MatHandler

class Normalizer(MatHandler):

  def resolve(self)->STDOut:
    self._setup()
    avail_entities = []

    try:
      for entity in self._entities:
        stdout = self._get_entity_error(entity)
        if stdout.code==200:
          self._normalize(entity)
          avail_entities.append(entity)
        else:
          self._mark(entity)
          self._logger.warning(f'[{self.__class__.__name__}] Skip a invalid entity - {entity["mat_title"]} - {stdout.message}')

      self._request['entities'] = avail_entities
      stdout = STDOut(200,'ok',avail_entities) if avail_entities else STDOut(500,'all are invalid')
      self._log(stdout)
      return stdout

    except Exception as e:
      message = f'[{self.__class__.__name__}] Failed to normalized any entities - {e}'
      self._logger.error(message)
      return STDOut(500,message)
    
  def _get_entity_error(self,entity:dict):
    if not entity.get('mat_url'):
      return STDOut(400,'Received an empty mat_url')
    if not entity.get('mat_title'):
      return STDOut(400,'Received an empty mat_title')
    return STDOut(200,'ok')

  def _normalize(self,entity):
    self._set_system_fileds(entity)
    # set for detail only
    self._set_paras(entity)
  
  def _set_system_fileds(self,entity):
    config = self._config.get('formatter',{})
    entity.setdefault('mat_chan',config.get('chan','article'))  # article gallery shortvideo qa
    entity.setdefault('mat_lang',config.get('lang','cn')) # cn en
    entity.setdefault('mat_id',BluesAlgorithm.md5(entity['mat_url'])) # md5
    entity.setdefault('mat_site',BluesURL.get_main_domain(entity['mat_url'])) # ifeng bbc

  def _set_paras(self,entity:dict):
    rows = entity.get('mat_paras')
    if not rows:
      return

    paras:List[dict] = []
    for row in rows: 
      image = row.get('image')
      text = row.get('text')
      if image:
        paras.append({'type':'image','value':image})
      else:
        paras.append({'type':'text','value':text})
    entity['mat_paras'] = paras


import sys,os,re
from urllib.parse import urlparse
from typing import List
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from material.MatHandler import MatHandler
from type.output.STDOut import STDOut
from material.file.MatFile import MatFile
from util.BluesAlgorithm import BluesAlgorithm
from util.BluesURL import BluesURL

class Localizer(MatHandler):

  def resolve(self)->STDOut:
    self._setup()
    config = self._config.get('privatizer')
    if not config:
      return STDOut(200,'no privatizer config')

    avail_entities = []

    try:
      for entity in self._entities:
        is_success = self._set_asset(entity)
        if is_success:
          avail_entities.append(entity)
        else:
          self._mark(entity)
          self._logger.warning(f'[{self.__class__.__name__}] Skip a unlocalized entity - {entity["mat_title"]}')

      self._request['entities'] = avail_entities
      stdout = STDOut(200,'ok',avail_entities) if avail_entities else STDOut(500,'all are unlocalized')
      self._log(stdout)
      return stdout

    except Exception as e:
      message = f'[{self.__class__.__name__}] Failed to localize - {e}'
      self._logger.error(message)
      return STDOut(500,message)
    
  def _is_http_url(self,url: str) -> bool:
    try:
      result = urlparse(url)
      # 检查 scheme 是否为 http 或 https，并且 netloc（域名）不为空
      return result.scheme in ('http', 'https') and bool(result.netloc)
    except ValueError:
      return False
    
  def _set_asset(self,entity:dict)->bool:
    self._set_thumbnail(entity)
    is_success = self._set_body_images(entity)
    if is_success and entity.get('mat_thumb'):
      return True
    else:
      return False
    
  def _set_thumbnail(self,entity)->bool:
      # convert online image to local image
      url = entity.get('mat_thumb')
      if not self._is_http_url(url):
        return False

      dft_id = BluesAlgorithm.md5(entity['mat_url'])
      dft_site = BluesURL.get_main_domain(entity['mat_url']) # ifeng bbc
      site = entity.get('mat_site',dft_site)
      id = entity.get('mat_id',dft_id)
      stdout = MatFile.get_download_image(site,id,url)
      if stdout.code==200:
        entity['mat_thumb'] = stdout.data
        return True 
      else:
        self._logger.warning(f'[{self.__class__.__name__}] {stdout.message} - {stdout.data}')
        return False

  def _set_body_images(self,entity:dict)->bool:
    config = self._config.get('privatizer') or {}
    max_image_count = config.get('max_image_count',-1)
    paras = entity.get('mat_paras')
    if not paras:
      return True # don't need to set body images

    image_count = 0

    images:List[str] = [] 
    for para in paras:
      # download and deal image
      success = self._download(entity,para,images)
      if success:
        image_count+=1
      if max_image_count!=-1 and image_count>=max_image_count:
        break

    self._pad_image(entity,images)
    self._pad_thumbnail(entity,images)
    return image_count>0
    
  def _download(self,entity:dict,para:dict,images:List[str])->bool:
    if para['type'] != 'image':
      return False

    site = entity.get('mat_site')
    id = entity.get('mat_id')
    url = para['value']
    if not self._is_http_url(url):
      return False
    stdout = MatFile.get_download_image(site,id,url)
    if stdout.code!=200:
      self._logger.error(f'[{self.__class__.__name__}] {stdout.message} - {stdout.data}')
      return False

    para['value'] = stdout.data
    images.append(stdout.data)
    return True

  def _pad_image(self,entity:dict,images:List[str]):
    mat_thumb = entity.get('mat_thumb')
    paras = entity.get('mat_paras')
    if not images and mat_thumb:
      paras.append({'type':'image','value':mat_thumb})
  
  def _pad_thumbnail(self,entity:dict,images:List[str]):
    if not entity.get('mat_thumb') and images:
      entity['mat_thumb'] = images[0]

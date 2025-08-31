import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.chain.AllMatchHandler import AllMatchHandler
from type.output.STDOut import STDOut
from material.formatter.Normalizer import Normalizer
from material.formatter.Validator import Validator
from material.formatter.Deduplicator import Deduplicator
from material.privatizer.Localizer import Localizer
from material.sinker.Sinker import Sinker

class MatHanderChain(AllMatchHandler):
  
  def resolve(self)->STDOut:
    try:
      chain = self._get_chain()
      stdout = chain.handle()
      # parse the request entities
      if stdout.code!=200:
        return stdout
      else:
        return STDOut(200,'ok',self._request['entities'])
    except Exception as e:
      message = f'[{self.__class__.__name__}] Failed to format - {e}'
      self._logger.error(message)
      return STDOut(500,message)
  
  def _get_chain(self)->AllMatchHandler:
    normalizer = Normalizer(self._request)
    deduplicator = Deduplicator(self._request)
    validator = Validator(self._request)
    localizer = Localizer(self._request)
    sinker = Sinker(self._request)
    
    normalizer.set_next(deduplicator).set_next(validator).set_next(localizer).set_next(sinker)
    return normalizer

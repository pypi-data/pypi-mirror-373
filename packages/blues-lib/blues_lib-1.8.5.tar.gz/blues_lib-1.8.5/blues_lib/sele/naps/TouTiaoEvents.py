import sys,os,re

from .NAPS import NAPS
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from plan.PublishPlanFactory import PublishPlanFactory     
from model.models.TouTiaoDBModelFactory import TouTiaoDBModelFactory
from loginer.factory.TouTiaoLoginerFactory import TouTiaoLoginerFactory   

class TouTiaoEvents(NAPS):

  CHANNEL = 'toutiao'

  def _get_plan(self):
    return PublishPlanFactory().create_toutiao({
      'events':1,
    })
    
  def _get_loginer(self):
    loginer_factory = TouTiaoLoginerFactory()
    return loginer_factory.create_persistent_mac()

  def _get_models(self):
    query_condition = {
      'mode':'latest',
      'material_type':'article',
      'count':self._plan.current_total,
    }
    factory = TouTiaoDBModelFactory()
    return factory.create_events(query_condition)

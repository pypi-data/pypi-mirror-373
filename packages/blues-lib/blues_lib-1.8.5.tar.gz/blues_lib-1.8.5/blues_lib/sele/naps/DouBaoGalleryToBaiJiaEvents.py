import sys,os,re

from .NAPS import NAPS
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from plan.PublishPlanFactory import PublishPlanFactory     
from model.models.BaiJiaDBModelFactory import BaiJiaDBModelFactory
from loginer.factory.BaiJiaLoginerFactory import BaiJiaLoginerFactory   
from schema.reader.doubao.DouBaoSchemaFactory import DouBaoSchemaFactory     
from sele.spider.MaterialSpider import MaterialSpider    

class DouBaoGalleryToBaiJiaEvents(NAPS):

  CHANNEL = 'baijia'

  def _get_plan(self):
    return PublishPlanFactory().create_baijia({
      'events':1,
    })
    
  def _get_loginer(self):
    loginer_factory = BaiJiaLoginerFactory()
    return loginer_factory.create_persistent_mac()

  def _get_models(self):
    query_condition = {
      'mode':'latest',
      'material_type':'gallery',
      'count':self._plan.current_total,
    }
    factory = BaiJiaDBModelFactory()
    return factory.create_events(query_condition)

  def spide(self):
    '''
    Crawl a material
    Return:
      {bool}
    '''
    factory = DouBaoSchemaFactory()
    schemas = factory.create_gallery_list()
    spider = MaterialSpider(schemas,self._plan.current_total,persistent=True)
    return spider.spide() 

 



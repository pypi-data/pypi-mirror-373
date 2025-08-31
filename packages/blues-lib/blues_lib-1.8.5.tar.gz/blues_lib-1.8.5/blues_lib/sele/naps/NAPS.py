import sys,os,re
from abc import ABC,abstractmethod
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from schema.reader.ifeng.IFengSchemaFactory import IFengSchemaFactory
from schema.reader.thepaper.ThePaperSchemaFactory import ThePaperSchemaFactory
from spider.MaterialSpider import MaterialSpider    
from publisher.StandardPublisher import StandardPublisher
from util.BluesConsole import BluesConsole

class NAPS(ABC):
  
  CHANNEL = ''

  '''
  1. Crawl a materail
  2. Login the publish page
  3. Publish
  4. Set published log
  '''
  def __init__(self):
    # {PublishPlan} current_quota current_total
    self._plan = self._get_plan()
  
  def execute(self):
    if self.__should_prevent():
      return

    self.spide()
    self.publish()
  
  def publish(self):
    if self.__should_prevent():
      return

    publisher = self.__get_publisher()
    publisher.publish()

  def prepublish(self):
    if self.__should_prevent():
      return

    publisher = self.__get_publisher()
    publisher.prepublish()

  def __get_publisher(self):
    loginer = self._get_loginer()
    models = self._get_models()
    return StandardPublisher(models,loginer)

  def __should_prevent(self):
    if self._plan.current_total<=0:
      BluesConsole.error('[%s] The limit for the day has been used up' % self.CHANNEL)
      return True
    else:
      return False

  @abstractmethod
  def _get_plan(self):
    pass

  @abstractmethod
  def _get_loginer(self):
    pass

  @abstractmethod
  def _get_models(self):
    pass

  def spide(self):
    '''
    Crawl a material
    Return:
      {bool}
    '''
    factory = ThePaperSchemaFactory()
    schema1 = factory.create_news('intl')

    factory = IFengSchemaFactory()
    schema2 = factory.create_tech_news()
    schema3 = factory.create_tech_outpost()
    schema4 = factory.create_hot_news()

    schemas = [schema2,schema3,schema4,schema1]

    spider = MaterialSpider(schemas,self._plan.current_total)
    return spider.spide()
 



import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.factory.Factory import Factory
from type.model.Model import Model
from sele.browser.Browser import Browser 
from crawler.base.BaseCrawlerFactory import BaseCrawlerFactory
from crawler.dfs.DfsCrawlerFactory import DfsCrawlerFactory
from namespace.CrawlerName import CrawlerName

class CrawlerFactory(Factory):

  _factory_classes = [BaseCrawlerFactory,DfsCrawlerFactory]

  def __init__(self,model:Model,browser:Browser) -> None:
    '''
    @param model {Model} : the model of crawler
    @param browser {Browser} : the browser instance to use
    '''
    self._model = model
    self._browser = browser

  def create(self,name:CrawlerName):
    for factory_class in self._factory_classes:
      factory:Factory = factory_class(self._model,self._browser)
      if crawler := factory.create(name):
        return crawler
    return None

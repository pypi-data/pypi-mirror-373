import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.factory.Factory import Factory
from type.model.Model import Model
from sele.browser.Browser import Browser 
from crawler.dfs.DepthCrawler import DepthCrawler
from namespace.CrawlerName import CrawlerName

class DfsCrawlerFactory(Factory):

  _crawlers = {
    DepthCrawler.NAME:DepthCrawler,
  }

  def __init__(self,model:Model,browser:Browser) -> None:
    '''
    @param model {Model} : the model of crawler
    @param browser {Browser} : the browser instance to use
    '''
    self._model = model
    self._browser = browser

  def create(self,name:CrawlerName):
    crawler = self._crawlers.get(name)
    if not crawler:
      return None
    return crawler(self._model,self._browser)

import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.output.STDOut import STDOut
from type.model.Model import Model
from namespace.CrawlerName import CrawlerName
from crawler.base.BaseCrawler import BaseCrawler

class UrlCrawler(BaseCrawler):

  NAME = CrawlerName.Engine.URL
    
  def _crawl(self)->STDOut:
    '''
    override the crawl method
    @return {STDOut}
    '''
    if not self._crawler_conf:
      message = f'[{self.NAME}] Failed to crawl - Missing crawler config'
      return STDOut(500,message)

    model = Model(self._crawler_conf)
    return self._invoke(model)

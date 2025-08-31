import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from behavior.BhvExecutor import BhvExecutor
from type.output.STDOut import STDOut
from type.model.Model import Model
from namespace.CrawlerName import CrawlerName
from crawler.Crawler import Crawler

class BaseCrawler(Crawler):

  def _before_crawled(self):
    # crawler
    self._crawler_meta = self._meta.get(CrawlerName.Field.CRAWLER.value)
    self._crawler_conf = self._conf.get(CrawlerName.Field.CRAWLER.value)

  def _invoke(self,model:Model)->STDOut:
    try:
      bhv = BhvExecutor(model,self._browser)
      stdout:STDOut = bhv.execute()
      if isinstance(stdout.data,dict):
        stdout.data = stdout.data.get(CrawlerName.Field.DATA.value)
      return stdout
    except Exception as e:
      message = f'[{self.NAME}] Failed to crawl - {e}'
      self._logger.error(message)
      return STDOut(500,message)
  
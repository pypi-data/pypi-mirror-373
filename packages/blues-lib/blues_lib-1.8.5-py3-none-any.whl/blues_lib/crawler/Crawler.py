import sys,os,re
from abc import abstractmethod
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.executor.Executor import Executor
from type.output.STDOut import STDOut
from type.model.Model import Model
from sele.browser.Browser import Browser 
from namespace.CrawlerName import CrawlerName

class Crawler(Executor):

  def __init__(self,model:Model,browser:Browser) -> None:
    '''
    @param model {Model} : the model of crawler
    @param browser {Browser} : the browser instance to use
    '''
    super().__init__()
    self._model:Model = model
    self._browser:Browser = browser

  def _setup(self):
    # model
    self._conf = self._model.config
    self._meta = self._model.meta
    self._bizdata = self._model.bizdata
    
    # summary
    self._summary_conf = self._conf.get(CrawlerName.Field.SUMMARY.value,{})
    self._count :int = self._summary_conf.get(CrawlerName.Field.COUNT.value,-1)
    # by default, quit the browser after crawled
    self._quit :bool = self._summary_conf.get(CrawlerName.Field.QUIT.value,True)
    
    # hook
    self._before_crawled_conf = self._conf.get(CrawlerName.Field.BEFORE_CRAWLED.value,{})
    self._after_crawled_conf = self._conf.get(CrawlerName.Field.AFTER_CRAWLED.value,{})
    self._before_each_crawled_conf = self._conf.get(CrawlerName.Field.BEFORE_EACH_CRAWLED.value,{})
    self._after_each_crawled_conf = self._conf.get(CrawlerName.Field.AFTER_EACH_CRAWLED.value,{})

  def execute(self)->STDOut:
    # Template method: define the cal structure
    self._setup()
    
    self._before_crawled()
    output:STDOut = self._crawl()
    self._after_crawled(output)

    self._slice(output)
    self._close()
    self._log(output)
    return output

  @abstractmethod
  def _crawl(self)->STDOut:
    pass
  
  def _before_crawled(self):
    pass

  def _after_crawled(self,output:STDOut):
    pass

  def _slice(self,output:STDOut):
    # slice the data by the config count

    if self._count==-1 or output.code!=200:
      return
    
    if not output.data or not isinstance(output.data,list):
      return

    output.data = output.data[:self._count]
  
  def _log(self,output:STDOut):
    if output.code != 200:
      message = f'[{self.NAME}] Failed to crawl - {output.message}'
      self._logger.error(message)
    else:
      message = f'[{self.NAME}] Managed to crawl'
      self._logger.info(message)

  def _open(self,url:str):
    self._browser.open(url)

  def _close(self):
    if self._quit and self._browser:
      self._browser.quit()
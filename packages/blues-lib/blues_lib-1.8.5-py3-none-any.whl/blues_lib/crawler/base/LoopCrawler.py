import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.output.STDOut import STDOut
from type.model.Model import Model
from crawler.base.BaseCrawler import BaseCrawler
from namespace.CrawlerName import CrawlerName

class LoopCrawler(BaseCrawler):

  NAME = CrawlerName.Engine.LOOP
  
  def _before_crawled(self):
    super()._before_crawled()
    self._set_entities_and_urls()
    
  def _set_entities_and_urls(self)->None:
    '''
    Create a standard input entities
    @param entities {list[dict]} the input entities
    @return {list[dict]} the standard input entities
    '''
    entities:list[dict] = self._summary_conf.get(CrawlerName.Field.ENTITIES.value) 
    urls:list[str] = self._summary_conf.get(CrawlerName.Field.URLS.value)
    url:str = self._summary_conf.get(CrawlerName.Field.URL.value)

    if entities and isinstance(entities,list):
      self._entities: list[dict] = [entity for entity in entities if entity.get(CrawlerName.Field.URL.value)]
      self._urls: list[str] = [entity.get(CrawlerName.Field.URL.value) for entity in self._entities]
      return 

    if not urls and url:
      urls = [url]
      
    if not urls:
      self._entities: list[dict] = []
      self._urls: list[str] = []
      return
    
    self._entities: list[dict] = [{} for _ in urls]
    self._urls: list[str] = urls

  def _crawl(self)->STDOut:
    if not self._crawler_meta:
      message = f'[{self.NAME}] Failed to crawl - Missing crawler meta'
      return STDOut(500,message)

    if not self._urls:
      message = f'[{self.NAME}] Failed to crawl - No available urls or entities (must has the url field) config'
      return STDOut(500,message)
    
    rows:list[dict] = self._crawl_by_urls()
    if rows:
      return STDOut(200,'done',rows)
    else:
      message = f'[{self.NAME}] Failed to crawl - No available data crawled'
      return STDOut(500,message)

  def _crawl_by_urls(self)->list[dict]:

    rows:list[dict] = []
    for index,url in enumerate(self._urls):

      entity:dict = self._entities[index]
      model:Model = self._get_model(url)
      output:STDOut = self._invoke(model)

      sub_rows:list[dict] = self._merge(output,entity)
      if not sub_rows:
        continue

      sub_output = STDOut(200,'deal the sub rows before count',sub_rows)
      
      # loop hook
      self._after_each_crawled(sub_output)

      if sub_output.code == 200 and sub_output.data:
        rows.extend(sub_output.data)
      
      if self._count != -1 and len(rows) >= self._count:
        break

    return rows
  
  def _after_each_crawled(self,output:STDOut)->None:
    # template method
    pass

  def _merge(self,output:STDOut,entity:dict)->list[dict]:
    if output.code != 200 or not output.data:
      return []

    sub_rows:list[dict] = output.data if isinstance(output.data, list) else [output.data]
    for sub_row in sub_rows:
      sub_row.update(entity)
    return sub_rows

  def _get_model(self,url:str)->Model:
    bizdata = {
      **self._bizdata,
      CrawlerName.Field.URL.value:url, # crawl the next url
    } 
    
    # remove the teardown to avoid to quit the browser before crawl all urls
    return Model(self._crawler_meta,bizdata)
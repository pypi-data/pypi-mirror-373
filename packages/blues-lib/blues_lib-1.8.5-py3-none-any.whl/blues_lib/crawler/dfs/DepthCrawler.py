import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.output.STDOut import STDOut
from type.model.Model import Model
from namespace.CrawlerName import CrawlerName
from crawler.Crawler import Crawler
from crawler.base.BaseCrawlerFactory import BaseCrawlerFactory

class DepthCrawler(Crawler):

  NAME = CrawlerName.Engine.DEPTH

  def _before_crawled(self):
    super()._before_crawled()
    # crawler
    self._metas:list[dict] = self._meta.get(CrawlerName.Field.METAS.value,[])
    # url
    self._pages:list[dict] = self._get_pages()
    # calculate
    self._max_depth:int = len(self._metas)
    self._rows:list[dict] = []
    
  def _get_pages(self)->list[dict]:
    pages:list[dict] = self._summary_conf.get(CrawlerName.Field.PAGES.value,[])
    if pages:
      return [page for page in pages if page.get('url')]
    
    urls:list[str] = self._summary_conf.get(CrawlerName.Field.URLS.value,[])
    url:str = self._summary_conf.get(CrawlerName.Field.URL.value)
    urls = urls if urls else ([url] if url else [])
    if not urls:
      return urls

    pages:list[dict] = []
    for url in urls:
      if not url:
        continue
      pages.append({
        "url":url,
        "bizdata":{}, # must be a dict
      })

    return pages
    
  def _crawl(self)->STDOut:
    '''
    override the crawl method
    @return {STDOut}
    '''
    if not self._metas:
      message = f'[{self.NAME}] Failed to crawl - Missing metas config'
      return STDOut(500,message)
    
    if not self._pages:
      message = f'[{self.NAME}] Failed to crawl - Missing pages config'
      return STDOut(500,message)

    # loop out of the dps, make sure Deep First Search
    depth = 1
    for page in self._pages:
      model = self._get_urls_replaced_model(page,depth)
      self._dfs(model,depth)
      if self._count != -1 and len(self._rows) >= self._count:
        break
      
    if self._rows:
      return STDOut(200,'success',self._rows)
    else:
      message = f'[{self.NAME}] Failed to crawl - No available entities found'
      return STDOut(500,message)

  def _dfs(self,model:Model,depth:int):

    # crawl : loop crawler will merge the entity to the output.data
    crawler_type = model.config.get('summary',{}).get(CrawlerName.Field.TYPE.value,CrawlerName.Engine.LOOP.value)
    crawler_name:CrawlerName = CrawlerName.Engine.from_value(crawler_type)
    crawler = BaseCrawlerFactory(model,self._browser).create(crawler_name)
    output:STDOut = crawler.execute()

    if output.code!=200 or not output.data:
      return

    if depth == self._max_depth:
      # add the entity to the rows
      self._rows.extend(output.data)
      return 
    
    next_depth = depth+1
    # loop for Deep First Search
    for entity in output.data:
      model = self._get_entities_replaced_model(entity,next_depth)
      self._dfs(model,next_depth)
      
  def _get_entities_replaced_model(self,entity:dict,depth:int)->Model:
    bizdata = {
      **self._bizdata,
      CrawlerName.Field.ENTITIES.value:[entity],
    } 

    meta = self._metas[depth-1]
    return Model(meta,bizdata)

  def _get_urls_replaced_model(self,page:dict,depth:int)->Model:
    url:str = page.get('url')
    page_bizdata:dict = page.get('bizdata')
    bizdata = {
      **self._bizdata,
      **page_bizdata, # page bizdata cover the main bizdata
      CrawlerName.Field.URLS.value:[url], 
    } 

    meta = self._metas[depth-1]
    return Model(meta,bizdata)


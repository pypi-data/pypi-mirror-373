import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.output.STDOut import STDOut
from crawler.base.LoopCrawler import LoopCrawler
from material.MatHanderChain import MatHanderChain

from namespace.CrawlerName import CrawlerName

class MatLoopCrawler(LoopCrawler):

  NAME = CrawlerName.Engine.MAT_LOOP
  
  def _after_each_crawled(self,output:STDOut)->None:
    '''
    Format the rows after one loop, before count
    '''
    if output.code!=200 or not output.data:
      return 

    request = {
      'config':self._after_each_crawled_conf,
      'entities':output.data,
    }
    handled_output:STDOut = MatHanderChain(request).handle()
    if handled_output.code == 200 and handled_output.data:
      output.code = 200
      output.data = handled_output.data
    else:
      output.code = 500
      output.message = handled_output.message
      output.data = []
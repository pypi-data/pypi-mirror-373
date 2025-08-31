import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from command.NodeCommand import NodeCommand
from type.output.STDOut import STDOut
from crawler.CrawlerFactory import CrawlerFactory
from namespace.CommandName import CommandName
from namespace.CrawlerName import CrawlerName

class Engine(NodeCommand):

  NAME = CommandName.Crawler.ENGINE
  TYPE = CommandName.Type.SETTER

  def _setup(self)->bool:
    super()._setup()
    br_output:STDOut = self._context[CommandName.Browser.CREATOR.value]
    if not br_output or br_output.code!=200:
      raise Exception(f'[{self.NAME}] browser output is None')
  
    self._browser = self._context[CommandName.Browser.CREATOR.value].data
    self._type:str = self._summary.get(CrawlerName.Field.TYPE.value,CrawlerName.Engine.URL.value)
    self._crawler_name:CrawlerName = CrawlerName.Engine.from_value(self._type)

  def _invoke(self)->STDOut:
    crawler = CrawlerFactory(self._node_input,self._browser).create(self._crawler_name)
    return crawler.execute()
    
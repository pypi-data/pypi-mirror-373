import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from namespace.CrawlerName import CrawlerName
from command.hook.processor.Processor import Processor
from command.hook.processor.prev.PrevProcFactory import PrevProcFactory

class PrevProcessor(Processor):
  
  POSITION = CrawlerName.Field.PREV

  def _get_proc_inst(self,class_name:str):
    return PrevProcFactory(self._context,self._input,self._proc_conf,self._name).create(class_name)

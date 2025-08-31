import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from command.hook.processor.Processor import Processor
from command.hook.processor.post.PostProcFactory import PostProcFactory
from type.model.Model import Model
from type.output.STDOut import STDOut
from namespace.CrawlerName import CrawlerName
from namespace.CommandName import CommandName

class PostProcessor(Processor):
  
  POSITION = CrawlerName.Field.POST

  def __init__(self,context:dict,input:Model,output:STDOut,name:CommandName) -> None:
    '''
    @param {dict} context : the flow's context
    @param {Model} input : the basic command node's input
    @param {CommandName} name : the current command's name
    '''
    super().__init__(context,input,name)
    self._output = output

  def _get_proc_inst(self,class_name:str):
    return PostProcFactory(self._context,self._input,self._proc_conf,self._output,self._name).create(class_name)

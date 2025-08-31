import sys,os,re
from abc import ABC,abstractmethod
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.executor.Executor import Executor
from type.model.Model import Model
from namespace.CrawlerName import CrawlerName
from namespace.CommandName import CommandName

class Processor(Executor):
  
  POSITION = None

  def __init__(self,context:dict,input:Model,name:CommandName) -> None:
    '''
    @param {dict} context : the flow's context
    @param {Model} input : the basic command node's input
    @param {CommandName} name : the current command's name
    '''
    super().__init__()
    self._context:dict = context
    self._input = input
    self._name = name
    # only the basic command has the processor conf
    self._proc_conf:dict = self._get_conf()
    
  def execute(self)->None:
    if not self._proc_conf:
      return

    type = self._proc_conf.get('type')
    value = self._proc_conf.get('value')
    if not type or not value:
      return

    self._proc_class(type,value)
    self._proc_script(type,value)
    
  def _proc_class(self,type:str,value:str):
    '''
    @description: exec by the predefined class
    @param {str} type : the processor type
    @param {str} value : the processor class name
    '''
    if type != 'class':
      return

    if processor := self._get_proc_inst(value):
      processor.execute()
    else:
      self._logger.warning(f'[{self._name}] processor {value} not found')
      
  @abstractmethod
  def _get_proc_inst(self,class_name:str):
    pass

  def _proc_script(self,type:str,script:str):
    '''
    @description: exec by the python script
    @param {str} type : the processor type
    @param {str} script : the processor script str
    '''
    if type != 'script':
      return

  def _get_conf(self)->dict|None:
    hook_conf = self._input.config.get(self.POSITION.value,{})
    return hook_conf.get(CrawlerName.Field.PROCESSOR.value)

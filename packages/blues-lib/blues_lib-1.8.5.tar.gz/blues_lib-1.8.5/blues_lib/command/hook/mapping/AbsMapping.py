import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.executor.Executor import Executor
from type.model.Model import Model
from type.output.STDOut import STDOut
from namespace.CrawlerName import CrawlerName
from namespace.CommandName import CommandName
from util.NestedDataMapping import NestedDataMapping

class AbsMapping(Executor):
  
  POSITION = None
  
  def __init__(self,context:dict,input:Model,name:CommandName):
    '''
    @param {dict} context : the flow's context
    @param {Model} input : the basic command node's input
    @param {CommandName} name : the current command's name
    '''
    self._context:dict = context
    self._input = input
    self._name = name
    # only model input can have a mapping config
    self._map_conf = self._get_conf()
  
  def _get_conf(self)->dict|None:
    hook_conf = self._input.config.get(self.POSITION.value,{})
    return hook_conf.get(CrawlerName.Field.MAPPING.value)

  def execute(self) -> bool:
    if not self._map_conf:
      return False

    source:dict = self._map_conf.get('source')
    target:dict = self._map_conf.get('target')
    method:str = self._map_conf.get('method','assign')

    if not target or not source:
      return False

    # both source and target can have a empty path 
    source_path:str = source.get('path')
    target_path:str = target.get('path')

    # the io.output is the default source data 
    source_command:str = source.get('command',CommandName.IO.OUTPUT.value)
    # the current command it the target data
    target_command:str = target.get('command',self._name.value)
    if not source_command or not target_command:
      return False 

    source_stdout:STDOut = self._context.get(source_command)
    if not source_stdout or not (source_data := source_stdout.data):
      return False
    
    target_data = self._get_target_data(target_command)

    if has_mapped:= NestedDataMapping.map(source_data,source_path,target_data,target_path,method):
      self._input.refresh()

    return has_mapped
    
  def _get_target_data(self,target_command:str):
    if target_command == self._name.value:
      target_data = self._input.bizdata
    else:
      stdout = self._context.get(target_command)
      target_data = stdout.data if stdout else None
    
    return target_data
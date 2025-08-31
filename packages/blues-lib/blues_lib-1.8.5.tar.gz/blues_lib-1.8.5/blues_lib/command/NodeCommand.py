import sys,os,re
from abc import abstractmethod
from typing import final,Any
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.executor.Command import Command
from namespace.CommandName import CommandName
from namespace.CrawlerName import CrawlerName
from type.output.STDOut import STDOut
from type.model.Model import Model
from command.hook.mapping.PrevMapping import PrevMapping
from command.hook.mapping.PostMapping import PostMapping
from command.hook.processor.PrevProcessor import PrevProcessor
from command.hook.processor.PostProcessor import PostProcessor

class NodeCommand(Command):

  NAME = CommandName.Exception.UNSET # should be rewrite by the subclass
  TYPE = CommandName.Type.ACTION

  INPUT = CommandName.IO.INPUT
  OUTPUT = CommandName.IO.OUTPUT 
  
  def __init__(self,context:dict,input:list[dict]|Model) -> None:
    f'''
    Args:
      context (dict): the flow's context, the client pass a empty dict
      input (list[dict]|Model): when it's a sub flow command it's a list, otherwise it's a Model
    '''
    super().__init__(context)
    self._output:STDOut = None # context.output
    self._node_input:dict|Model = input # node's input
    self._is_flow:bool = not isinstance(input,Model)

  @final
  def execute(self):

    # prev hook
    if not self._is_flow:
      PrevMapping(self._context,self._node_input,self.NAME).execute()
      PrevProcessor(self._context,self._node_input,self.NAME).execute()

    # check and init fields
    self._setup()

    # execute the action and return the init stdout
    node_output:STDOut = self._invoke()

    # post process by factory
    if not self._is_flow:
      PostMapping(self._context,self._node_input,self.NAME).execute()
      PostProcessor(self._context,self._node_input,node_output,self.NAME).execute()

    self._export(node_output)
    self._raise(node_output)
    self._log(node_output)
    
  def _setup(self):
    if not self._node_input:
      raise Exception(f'[{self.NAME}] node input is None')

    # lazy to get the flow's output
    self._output = self._context.get(self.OUTPUT.value)

    # flow kind command's node input is a dict
    if not self._is_flow:
      self._node_conf:dict = self._node_input.config
      self._node_meta:dict = self._node_input.meta
      self._node_bizdata:dict = self._node_input.bizdata
      self._summary:dict = self._node_conf.get(CrawlerName.Field.SUMMARY.value,{})
      self._onerror:str = self._summary.get('onerror',CommandName.Exception.ABORT.value)
    else:
      # flow command don't abort the flow
      self._onerror:str = CommandName.Exception.IGNORE.value

  @abstractmethod
  def _invoke(self):
    pass

  def _export(self,stdout:STDOut):

    # add to the node output 
    self._context[self.NAME.value] = stdout
    # add to the flow output
    if self.TYPE == CommandName.Type.SETTER:
      self._context[self.OUTPUT.value] = stdout
      
  def _raise(self,stdout:STDOut):
    if stdout.code !=200 and self._onerror==CommandName.Exception.ABORT.value:
      raise Exception(stdout.message)

  def _log(self,stdout:STDOut):
    if stdout.code == 200:
      self._logger.info(stdout.message)
    else:
      self._logger.error(stdout.message)

import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from command.NodeCommand import NodeCommand
from namespace.CommandName import CommandName
from type.output.STDOut import STDOut
from material.sinker.Sinker import Sinker as SinkerHandler

class Sinker(NodeCommand):
  
  NAME = CommandName.Material.SINKER

  def _setup(self):
    super()._setup()
    if not self._output:
      message = f'[{self.NAME}] Failed to check - {self.OUTPUT} is not ok'
      raise Exception(message)

  def _invoke(self)->STDOut:
    entities:list[dict] = self._output.data if isinstance(self._output.data,list) else [self._output.data]
    request = {
      'config':{
        'sinker':self._summary,
      },
      'entities':entities, # must be a list
    } 
    handler = SinkerHandler(request)
    return handler.handle()

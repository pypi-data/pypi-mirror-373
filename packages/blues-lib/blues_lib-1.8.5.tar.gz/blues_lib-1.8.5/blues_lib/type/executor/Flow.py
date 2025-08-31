import sys,os,re
from typing import List
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.exception import FlowRetryException
from type.executor.Executor import Executor
from type.output.STDOut import STDOut
from type.exception.FlowBlockedException import FlowBlockedException
from namespace.CommandName import CommandName

class Flow(Executor):
  
  def __init__(self):
    super().__init__()
    self.context = {}
    self._executors:List[Executor] = []

  @property
  def size(self)->int:
    return len(self._executors)

  @property
  def executors(self)->List[Executor]:
    return self._executors
    
  def add(self,executor:Executor):
    self._executors.append(executor)

  def execute(self)->STDOut:
    if not self._executors:
      message = f'[{self.__class__.__name__}] Skip to execute the flow - no executors'
      self._logger.warning(message)
      return STDOut(200,message)

    try:
      for executor in self._executors:
        executor.execute()
        
      # the flow return the context's output
      return self.context[CommandName.IO.OUTPUT.value]

    except FlowBlockedException as e:
      message = f'[{self.__class__.__name__}] Managed to block the flow - {e}'
      self._logger.info(message)
      return STDOut(200,message)
    except FlowRetryException as e:
      message = f'[{self.__class__.__name__}] Retry the current flow - {e}'
      self._logger.info(message)
      return self.execute()

    except Exception as e:
      message = f'[{self.__class__.__name__}] Failed to execute the flow - {e}'
      self._logger.error(message)
      return STDOut(500,message)
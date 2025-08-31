import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.executor.Executor import Executor
from type.output.STDOut import STDOut
from type.model.Model import Model
from namespace.CommandName import CommandName

class AbsPrevProc(Executor):
  
  def __init__(self,context:dict,input:Model,proc_conf:dict,name:CommandName) -> None:
    super().__init__()
    self._context = context
    self._input = input
    self._proc_conf = proc_conf
    self._name = name
  
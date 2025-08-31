import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.factory.Factory import Factory
from type.model.Model import Model
from type.executor.Executor import Executor
from namespace.CommandName import CommandName
from command.hook.processor.prev.TextToAIQuery import TextToAIQuery

class PrevProcFactory(Factory):

  _proc_classes = {
    TextToAIQuery.__name__:TextToAIQuery,
  }

  def __init__(self,context:dict,input:Model,proc_conf:dict,name:CommandName) -> None:
    self._context = context
    self._input = input
    self._proc_conf = proc_conf
    self._name = name

  def create(self,proc_name:str)->Executor | None:
    # overide
    proc_class = self._proc_classes.get(proc_name)
    return proc_class(self._context,self._input,self._proc_conf,self._name) if proc_class else None



import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.executor.Executor import Executor

class Command(Executor):

  def __init__(self,context:dict):
    super().__init__()
    self._context = context

  @property
  def context(self):
    return self._context


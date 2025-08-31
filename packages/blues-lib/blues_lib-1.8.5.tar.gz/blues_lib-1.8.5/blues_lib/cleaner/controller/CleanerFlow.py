import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.executor.CommandFlow import CommandFlow
from cleaner.controller.command.DBCMD import DBCMD
from cleaner.controller.command.FileCMD import FileCMD

class CleanerFlow(CommandFlow):
  
  _default_context = {
    'db':{
      'material':{'validity_days':100,'response':None},
      'loginlog':{'validity_days':100,'response':None},
      'publog':{'validity_days':300,'response':None},
    },
    'file':{
      'material':{'validity_days':30,'response':None},
      'log':{'validity_days':30,'response':None},
    },
  }

  def __init__(self,context=None):
    super().__init__(context)
    if not context:
      self._context = self._default_context
  
  def load(self):

    db_cmd = DBCMD(self._context)
    file_cmd = FileCMD(self._context)

    self.add(db_cmd)
    self.add(file_cmd)
    










import sys,os,re

sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.executor.Command import Command
from cleaner.handler.db.DBCleanerChain import DBCleanerChain   

class DBCMD(Command):

  name = __name__

  def execute(self):
    DBCleanerChain().handle(self._context)

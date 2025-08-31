import sys,os,re

sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.executor.Command import Command
from cleaner.handler.file.FileCleanerChain import FileCleanerChain   

class FileCMD(Command):

  name = __name__

  def execute(self):
    FileCleanerChain().handle(self._context)



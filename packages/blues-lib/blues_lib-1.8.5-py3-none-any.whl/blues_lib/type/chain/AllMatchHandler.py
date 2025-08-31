import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.output.STDOut import STDOut
from type.chain.Handler import Handler

class AllMatchHandler(Handler):

  def handle(self)->STDOut:
    stdout = self.resolve()

    if self._next_handler:
      return self._next_handler.handle()
    else:
      return stdout


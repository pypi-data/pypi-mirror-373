import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.output.STDOut import STDOut
from type.chain.Handler import Handler

class FirstMatchHandler(Handler):

  def handle(self):
    stdout = self.resolve()
    if stdout.code==200:
      return stdout

    if self._next_handler:
      return self._next_handler.handle()

    return STDOut(500,'Failed to handle the request',None)

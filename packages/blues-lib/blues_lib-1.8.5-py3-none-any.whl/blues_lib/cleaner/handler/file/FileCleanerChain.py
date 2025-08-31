import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from cleaner.handler.CleanerHandler import CleanerHandler
from .MaterialHandler import MaterialHandler  
from .LogHandler import LogHandler  

class FileCleanerChain(CleanerHandler):

  kind = 'chain'

  def resolve(self,request):
    handler = self._get_chain()
    return handler.handle(request)

  def _get_chain(self):
    material_handler = MaterialHandler()
    log_handler = LogHandler()
    
    material_handler.set_next(log_handler)

    return material_handler

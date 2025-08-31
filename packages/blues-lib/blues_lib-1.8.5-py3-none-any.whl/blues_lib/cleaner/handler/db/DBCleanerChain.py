import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from cleaner.handler.CleanerHandler import CleanerHandler
from .MaterialHandler import MaterialHandler  
from .LoginLogHandler import LoginLogHandler  

class DBCleanerChain(CleanerHandler):

  kind = 'chain'

  def resolve(self,request):
    '''
    Deal the atom by the event chain
    '''
    handler = self._get_chain()
    return handler.handle(request)

  def _get_chain(self):
    material_handler = MaterialHandler()
    login_log_handler = LoginLogHandler()
    
    material_handler.set_next(login_log_handler)

    return material_handler

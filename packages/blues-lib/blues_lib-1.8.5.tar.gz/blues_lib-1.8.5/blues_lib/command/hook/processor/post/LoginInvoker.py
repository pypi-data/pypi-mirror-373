import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from command.hook.processor.post.AbsPostProc import AbsPostProc
from namespace.CrawlerName import CrawlerName

class LoginInvoker(AbsPostProc):
  
  def execute(self)->None:
    '''
    @description: check the login status
    @return: None
    '''
    if not self._output.data :
      self._output.code = 500
      self._output.message = 'valid login failed: has no output.data'
    elif not self._output.data.get(CrawlerName.Field.LOGGEDIN.value):
      self._output.code = 500
      self._output.message = 'valid login failed: loggedin is false'
    elif not (ckfile := self._output.data.get(CrawlerName.Field.CKFILE.value)):
      self._output.code = 500
      self._output.message = 'failed to save the cookies'
    else:
      self._output.message = f'login and save the cookies - {ckfile}'
  
  
  
   

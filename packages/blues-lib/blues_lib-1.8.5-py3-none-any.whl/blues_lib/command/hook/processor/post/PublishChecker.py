import sys,os,re
from datetime import datetime
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from command.hook.processor.post.AbsPostProc import AbsPostProc

class PublishChecker(AbsPostProc):
  
  def execute(self)->None:
    '''
    @description: check the login status
    @return: None
    '''
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    self._output.code = 500
    self._output.data['pub_stat'] = "failure"
    self._output.data['pub_time'] = current_time

    if not self._output.data :
      self._output.message = f'{self.__class__.__name__} publish failed: has no output.data'
    elif self._output.data.get('published'):
      self._output.code = 200
      self._output.data['pub_stat'] = "success"
      self._output.message = f'{self.__class__.__name__} publish success'
    else:
      self._output.message = f'{self.__class__.__name__} publish failed'


    
    
    
    
     

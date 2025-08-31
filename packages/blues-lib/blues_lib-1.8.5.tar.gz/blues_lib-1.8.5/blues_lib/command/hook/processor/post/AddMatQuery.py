import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from command.hook.processor.post.AbsPostProc import AbsPostProc

class AddMatQuery(AbsPostProc):
  
  PARAS_FIELD = 'mat_paras'
  
  def execute(self)->None:
    '''
    @description: Convert the mat to para text
    @return: None
    '''
    if self._output.data and isinstance(self._output.data,list):
      mat:dict = self._output.data[0]
      paras:list[dict] = mat.get(self.PARAS_FIELD)

      self._output.data = mat
      if paras and isinstance(paras,list):
        mat['query'] = self._join(paras)
      else:
        self._output.code = 500
        self._output.message = f'mat_paras is not a list, data: {self._output.data}'

  def _join(self,paras:list[dict])->str:
    text = ''
    for para in paras:
      if para.get('type') == 'text':
        text += para.get('value')
    return text

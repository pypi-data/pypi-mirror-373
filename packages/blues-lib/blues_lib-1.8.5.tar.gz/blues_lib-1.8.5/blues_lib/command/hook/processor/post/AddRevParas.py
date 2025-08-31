import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from command.hook.processor.post.AbsPostProc import AbsPostProc

class AddRevParas(AbsPostProc):
  
  def execute(self)->None:
    '''
    @description: Convert the mat to para text
    @return: None
    '''
    if self._output.data and isinstance(self._output.data,list):
      rows:list[dict] = self._output.data
      for row in rows:
        self._add(row)

  def _add(self,mat:dict):
    mat_paras:list[dict] = mat.get('mat_paras')
    rev_texts:list[dict] = mat.get('rev_texts')
    rev_title:list[dict] = mat.get('rev_title')
    if not mat_paras or not rev_texts:
      return
    
    images:list[dict] = []
    for mat_para in mat_paras:
      if mat_para.get('type') == 'image':
        images.append(mat_para)

    rev_paras = []
    for rev_text in rev_texts:
      rev_paras.append({
        'type':'text',
        'value':rev_text,
      })
      if images:
        image = images.pop(0)
        rev_paras.append(image)

    # cover the mat fields    
    mat['mat_paras'] = rev_paras
    mat['mat_title'] = rev_title





import sys,os,re
from typing import List
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.executor.Executor import Executor

class Extractor(Executor):
    
  def execute(self,answer:str)->dict:
    '''
    Convert the copied text to a format material dict
    @param answer: the AI answer
    @return: a dict with 'rev_title' and 'rev_texts'
    '''
    content = self._get_text(answer)
    texts = self._get_texts(content)
    # the first line is the title
    first_para = texts.pop(0)
    title = self._get_title(first_para)
    return {
      'rev_title':title,
      'rev_texts':texts,
    }

  def _get_texts(self,content:str)->List[str]:
    body = content.replace('"',"'")
    paras = re.split(r'[\n\r]', body)
    para_list = []
    for para in paras:
      text = para.strip()
      if not text:
        continue 
      # At least cotains one letter
      pattern = r'[a-zA-Z\u4e00-\u9fa5]'
      if re.search(pattern, text):
        para_list.append(text)
    return para_list

  def _get_text(self,context)->str:
    patterns = [
      r'^\**正文\**\s*[:：]?\s*(.+)', # **正文**: xxx
    ]

    text = context
    for pattern in patterns:
      matches = re.findall(pattern,text)
      if matches:
        text = matches[0]

    return text

  def _get_title(self,title)->str:
    patterns = [
      r'标题\s*[:：]?\s*(.+)', # 标题: xxx
      r'《(.+)》', # 标题：《xxx》
      r'\*+(.+)\*+', # **xxx**
    ]

    text = title
    for pattern in patterns:
      matches = re.findall(pattern,text)
      if matches:
        text = matches[0]

    # patter : ** xxx ** ; # xxxx
    return re.sub(r'[#*]', '', text).strip()
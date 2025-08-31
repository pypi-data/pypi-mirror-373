class AIPrompt:
  
  def __init__(self,prompt:dict,text:str):
    '''
    @description: 初始化AI提示
    @param prompt {dict} : 提示配置
      - role {list[str]} : 角色
      - rule {list[str]} : 规则
      - limit {list[str]} : 限制
    @param text {str} : 原文
    @return: str
    '''
    self._prompt = prompt
    self._text = text
    
  def get(self)->str:
    role = self.get_role()
    rule = self.get_rule()
    limit = self.get_limit()
    text = self.get_text()
    return f"{role}{rule}{limit}{text}"
  
  def get_text(self):
    return  f'文章内容如下：[{self._text}]'
  
  def get_role(self):
    texts = self._prompt.get('role')
    return self._join(texts)
    
  def get_rule(self):
    texts = self._prompt.get('rule')
    return self._join(texts)
    
  def get_limit(self):
    texts = self._prompt.get('limit')
    return self._join(texts)
    
  def _join(self,texts:list[str]):
    total = ""
    if not texts:
      return total

    for text in texts:
      total+=text
    return total
    
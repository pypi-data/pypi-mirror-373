import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from publisher.article.ArticlePublisher import ArticlePublisher

class PublisherFactory():
  '''
  Abstract Factory Mode, use best practices:
  1. Each specific class is created using an independent method
  2. Use instance usage and parameters as class fields
  '''
  
  def __init__(self,browser,schema):
    self._browser = browser
    self._schema = schema

  def create(self, mode: str):
    method_name = f"create_{mode.lower()}"
    if not hasattr(self, method_name):
      return None
    method = getattr(self, method_name)
    return method()

  def create_article(self):
    return ArticlePublisher(self._browser,self._schema)
  
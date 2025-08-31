import re
from .HttpMessageFilter import HttpMessageFilter

class URLFilter(HttpMessageFilter):

  def __init__(self,pattern=''):
    self.__pattern = pattern
    super().__init__()

  def resolve(self,messages):

    if not messages:
      return messages

    if not self.__pattern:
      return messages

    reqs = []
    for message in messages:
      url = message['request']['url']
      if re.search(self.__pattern,url):
        reqs.append(message)

    return reqs
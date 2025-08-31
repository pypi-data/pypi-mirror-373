from .HttpMessageFilter import HttpMessageFilter

class CountFilter(HttpMessageFilter):

  def __init__(self,count=-1):
    self.__count = count
    super().__init__()

  def resolve(self,messages):
    if not messages:
      return messages

    if self.__count==-1:
      return messages

    count = self.__count if self.__count>=0 else 0
    return messages[:count]
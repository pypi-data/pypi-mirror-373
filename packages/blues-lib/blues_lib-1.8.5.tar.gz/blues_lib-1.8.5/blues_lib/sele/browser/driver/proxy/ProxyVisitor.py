import abc
class ProxyVisitor(metaclass=abc.ABCMeta):

  @abc.abstractmethod
  def visit(self,proxy_message):
    pass
  
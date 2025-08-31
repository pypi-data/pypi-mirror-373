from abc import ABC
import inspect
from namespace.NSEnum import NSEnum

class EnumNS(ABC):
  @classmethod
  def from_value(cls,value:str)->NSEnum|None:
    label = value.replace('-','.')
    for name,subclass in inspect.getmembers(cls):
      if inspect.isclass(subclass) and issubclass(subclass,NSEnum):
        member = subclass.from_value(label)
        if member is not None:
          return member
    return None

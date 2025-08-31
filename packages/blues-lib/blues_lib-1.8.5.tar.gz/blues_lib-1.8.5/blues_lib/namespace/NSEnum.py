from enum import Enum

class NSEnum(Enum):

  # overriede __str__
  def __str__(self):
    return self.value
  
  @classmethod
  def from_value(cls, value: str):
    """通过字符串值获取对应的枚举成员"""
    try:
      # 直接使用 Enum 的内置机制
      return cls(value)  
    except ValueError:
      return None


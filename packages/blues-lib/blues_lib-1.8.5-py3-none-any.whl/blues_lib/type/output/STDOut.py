from dataclasses import dataclass, asdict
from typing import Any

@dataclass
class STDOut:
  code: int = 200
  message: str = 'success'
  data: Any = None
  detail: Any = None

  def to_dict(self)->dict:
    return asdict(self)

  def to_status(self)->tuple:
    return (self.code,self.message)
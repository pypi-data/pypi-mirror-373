from typing import Any
from dataclasses import dataclass, asdict

@dataclass
class SQLSTDOut():
  code:int = 200
  message:str = 'success'
  data: Any = None
  detail: Any = None
  count: int = 0
  sql: str = ''
  lastid: Any = None

  def to_dict(self)->dict:
    return asdict(self)
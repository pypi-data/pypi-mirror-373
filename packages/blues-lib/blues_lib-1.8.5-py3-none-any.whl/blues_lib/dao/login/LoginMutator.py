import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from dao.sql.TableMutator import TableMutator

class LoginMutator(TableMutator):
  
  _TABLE = 'naps_loginer'

  def __init__(self) -> None:
    super().__init__(self._TABLE)



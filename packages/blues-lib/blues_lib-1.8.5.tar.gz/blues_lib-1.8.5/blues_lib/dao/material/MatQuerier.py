import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.output.SQLSTDOut import SQLSTDOut
from dao.sql.TableQuerier import TableQuerier

class MatQuerier(TableQuerier):

  _TABLE = 'ap_mat'

  def __init__(self) -> None:
    super().__init__(self._TABLE)

  def exist(self,mat_id:str)->bool:
    fields = ['mat_id']
    conditions = [
      {
        'field':'mat_id',
        'comparator':'=',
        'value':mat_id,
      },
    ]
    stdout:SQLSTDOut = self.get(fields,conditions)
    return stdout.count>0

  def random(self,fields='*',conditions:list[dict]=None,size:int=1)->SQLSTDOut:
    '''
    @description: Get a random row
    @param {dict} query : the query dict,like:
      [
        {"field":"mat_chan","comparator":"=","value":"${mat_chan}"},
        {"field":"mat_stat","comparator":"=","value":"available","operator":"and"},
      ]
    @param {int} size : the size of the random rows
    @returns {SQLSTDOut}
    '''
    # get the latest
    orders = [{
      'field':'rand()',
      'sort':''
    }]
    # get one row
    pagination = {
      'no':1,
      'size':size
    }
    return self.get(fields,conditions,orders,pagination)

  def latest(self,fields='*',conditions:list[dict]=None,size:int=1)->SQLSTDOut:
    '''
    @description: Get the latest rows
    @param {list[dict]} conditions :
      [
        {"field":"mat_chan","comparator":"=","value":"${mat_chan}"},
        {"field":"mat_stat","comparator":"=","value":"available","operator":"and"},
      ]
    @param {int} size : the size of the latest rows
    @returns {SQLSTDOut}
    '''
    # get the latest
    orders = [{
      'field':'mat_ctime',
      'sort':'desc'
    }]
    # get one row
    pagination = {
      'no':1,
      'size':size
    }
    return self.get(fields,conditions,orders,pagination)

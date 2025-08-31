import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from namespace.CommandName import CommandName
from command.NodeCommand import NodeCommand
from dao.material.MatQuerier import MatQuerier
from type.output.STDOut import STDOut

class Querier(NodeCommand):

  NAME = CommandName.Material.QUERIER
  TYPE = CommandName.Type.SETTER

  def _invoke(self)->STDOut:
    querier = MatQuerier()
    fields = self._summary.get('fields','*')
    count = self._summary.get('count',1)
    conditions = self._summary.get('conditions')
    output:STDOut = querier.latest(fields,conditions,count)
    if not output.data:
      return STDOut(500,f'{self.NAME} No data found - {conditions}')
    return output



     
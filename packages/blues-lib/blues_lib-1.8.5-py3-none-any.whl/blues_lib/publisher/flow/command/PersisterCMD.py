import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.executor.Command import Command
from dao.material.MatMutator import MatMutator

class PersisterCMD(Command):

  name = __name__
  mutator = MatMutator()

  def execute(self):
    material = self._context['publisher'].get('material')
    pub_keys = ["material_status", "material_pub_shot", "material_pub_date", "material_pub_platform", "material_pub_channel"]
    entity = {key: material[key] for key in pub_keys if key in material}
    conditions = [
      {
        'field':'material_id',
        'comparator':'=',
        'value':material['material_id']
      }
    ]
    response = self.mutator.update(entity,conditions)
    self._context['publisher']['persister'] = response

    if response['code']!=200:
      raise Exception('Failed to update the status of the material!')

    if material['material_status'] != 'pubsuccess':
      raise Exception('Failed to publish!')


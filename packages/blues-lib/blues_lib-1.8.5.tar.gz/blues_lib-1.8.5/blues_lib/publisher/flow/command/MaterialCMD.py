import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.executor.Command import Command
from material.DBMaterial import DBMaterial     

class MaterialCMD(Command):

  name = __name__

  def execute(self):
    executor_schema = self._context['publisher']['schema'].get('executor')
    material_mode = executor_schema.basic.get('mode')
    query_condition = {
      'mode':'latest',
      'material_type':material_mode,
      'count':1,
    }
    material = DBMaterial().first(query_condition)
    if not material:
      raise Exception('[Publisher] Failed to get available materials from the DB!')

    status = self._is_legal(executor_schema,material)
    if not status:
      raise Exception('[Publisher] The material is not a ai row!')

    self._context['publisher']['material'] = material
    
  def _is_legal(self,executor_schema,material):
    field = executor_schema.basic.get('field')
    if field == 'ai':
      if not material.get('material_ai_title') or not material.get('material_ai_body_text'):
        return False
    return True

import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from dao.material.MatMutator import MatMutator
from cleaner.handler.CleanerHandler import CleanerHandler
from deco.LogDeco import LogDeco

class MaterialHandler(CleanerHandler):

  kind = 'handler'
  mutator = MatMutator()

  @LogDeco()
  def resolve(self,request):
    '''
    Args:
      {dict} request : 
        - {dict} material
          - {int} validity_days : by default is 100
          - {dict} response : cleared response
    Returns {dict} response
      - {int} code
      - {int} count
      - {str} message
    '''
    main_req = request.get('db')
    if not main_req:
      return 

    sub_req = main_req.get('material')
    if not sub_req:
      return 

    validity_days = sub_req.get('validity_days',100)
    conditions = [
      {
        'field':'material_collect_date',
        'comparator':'<=',
        'value':'DATE_SUB(CURRENT_DATE, INTERVAL %s DAY)' % validity_days,
        'value_type':'function',
      }
    ]
    response = self.mutator.delete(conditions)
    sub_req['response'] = response
    self.set_message(response)
    return response

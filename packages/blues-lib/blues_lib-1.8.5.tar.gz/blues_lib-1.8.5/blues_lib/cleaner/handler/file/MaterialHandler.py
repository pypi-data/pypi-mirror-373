import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from material.file.MatFile import MatFile
from cleaner.handler.CleanerHandler import CleanerHandler
from util.BluesFiler import BluesFiler
from deco.LogDeco import LogDeco

class MaterialHandler(CleanerHandler):

  kind = 'handler'

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
    main_req = request.get('file')
    if not main_req:
      return 

    sub_req = main_req.get('material')
    if not sub_req:
      return 

    root = MatFile.get_material_root()
    validity_days = sub_req.get('validity_days',30)
    count = BluesFiler.removedirs(root,validity_days)
    response = {
      'code':200,
      'count':count,
      'message':'Deleted materials.',
    }
    sub_req['response'] = response
    self.set_message(response)
    return response
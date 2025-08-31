import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from dao.login.LoginMutator import LoginMutator
from cleaner.handler.CleanerHandler import CleanerHandler
from deco.LogDeco import LogDeco

class LoginLogHandler(CleanerHandler):

  kind = 'handler'
  mutator = LoginMutator()

  @LogDeco()
  def resolve(self,request):
    '''
    Args:
      {dict} request: 
        - {dict} loginlog 
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

    sub_req = main_req.get('loginlog')
    if not sub_req:
      return 

    validity_days = sub_req.get('validity_days',100)
    conditions = [
      {
        'field':'login_created_time',
        'comparator':'<=',
        'value':'DATE_SUB(CURRENT_DATE, INTERVAL %s DAY)' % validity_days,
        'value_type':'function',
      }
    ]
    response = self.mutator.delete(conditions)
    sub_req['response'] = response
    self.set_message(response)
    return response

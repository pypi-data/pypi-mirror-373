import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from util.BluesDateTime import BluesDateTime
from behavior.bean.Bean import Bean
from dao.login.LoginQuerier import LoginQuerier
from type.model.Model import Model
from type.output.STDOut import STDOut

class AuthCodeInput(Bean):

  def _set(self)->bool:
    code = self._config['value']
    if not code or code == '__sentinel__':
      code = self._get()

    if not code:
      self._logger.error(f'[{self.__class__.__name__}] Failed to fetch the auth code')
      return False

    stdout = self._input(code)
    print('-->stdout',stdout)
    
    if stdout.code==200:
      self._logger.info(f'[{self.__class__.__name__}] Managed to fetch and input the auth code - {code}')
      return True
    else:
      self._logger.error(f'[{self.__class__.__name__}] Failed to input the auth code - {code} - {stdout.message}')
      return False

  def _input(self,code)->STDOut:
    from behavior.BhvExecutor import BhvExecutor

    input_conf = {
      '_kind':'input',
      'granularity':self._config.get('granularity','text'),
      'target_CS_WE':self._config.get('target_CS_WE'),
      'value':code,
    }
    model = Model(input_conf)
    executor = BhvExecutor(model,self._browser)
    return executor.execute()

  def _get(self)->str:
    '''
    Wait the code upload and continue
    '''
    step = 10
    code_expire = self._config.get('code_expire',300)
    domain = self._config.get('domain')
    ts = self._config.get('timestamp')
    steps =  list(range(0,code_expire,step)) 
    i = 0
    for s in steps:
      i+=1
      
      if code := self._get_code(domain,ts):
        return str(code) # must be a str

      BluesDateTime.count_down({
        'duration':step,
        'title':f'[{self.__class__.__name__}] Wait for the auth code {i*step}/{code_expire} - {domain} {ts}'
      })
    return ''

  def _get_code(self,domain,ts)->str:
    conditions = [
      {'field':'login_ts','comparator':'=','value':ts},
      {'field':'login_site','comparator':'=','value':domain},
    ]
    querier = LoginQuerier()
    stdout:STDOut = querier.get('*',conditions)
    data = stdout.data
    return data[0]['login_sms_code'] if data else ''

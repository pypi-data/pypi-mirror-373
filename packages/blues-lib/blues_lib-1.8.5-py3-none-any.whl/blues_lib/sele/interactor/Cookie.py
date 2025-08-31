import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from util.BluesURL import BluesURL  
from util.BluesConsole import BluesConsole  

# 提供Cookie相关功能
class Cookie():
  '''
  WebDriver API provides a way to interact with cookies
  Cookie doc: https://www.selenium.dev/documentation/webdriver/interactions/cookies/
  '''
 
  def __init__(self,driver):
    self.__driver = driver

  def __get_default_entity(self):
    current_domain = BluesURL.get_main_domain(self.__driver.current_url)
    return {
      'name':'',
      'value':'',
      'domain':'.%s' % current_domain, 
      'expires': '',
      'path': '/',
      'httpOnly': False,
      'hostOnly': False,
      'secure': False,
    }

  def get(self,name=''):
    '''
    Get a named cookie or all cookies
    Parameter:
      name {str} : cookie name
    Returns: cookie entity or entities
       - {'domain': 'mp.163.com', 'httpOnly': True, 'name': 'NTESwebSI', 'path': '/', 'sameSite': 'Lax', 'secure': False, 'value': '2A7C7F8FCD65F7D74650E13D349C60CC'}
       - [{'domain': 'mp.163.com', 'httpOnly': True, 'name': 'NTESwebSI', 'path': '/', 'sameSite': 'Lax', 'secure': False, 'value': '2A7C7F8FCD65F7D74650E13D349C60CC'}]
    '''
    if name:
      return self.__driver.get_cookie(name)
    else:
      return self.__driver.get_cookies()
      
  def add(self,entities):
    '''
    Add cookies to the current browsing context
    The list of accepted JSON key values : https://www.w3.org/TR/webdriver1/#cookies
    Parameter:
      entities {list<dict> | dict} : one or multi cookie entities, it's a format cookie dict
      - {'name':'sessionid', 'value':'1715957318'}
    Returns:
      {int} : The number of successful additions
    '''
    
    count = 0
    items = entities if type(entities)==list else [entities]
    for entity in items:
      if not entity.get('name'):
        continue
      count+=1
      full_entity = self.__get_complete_entity(entity)
      self.__driver.add_cookie(full_entity)
    return count

  def replace(self,entities:list[dict]):
    '''
    Replace the current cookies with the new cookies
    Parameter:
      entities {list<dict>} : the new cookie entities - standard cookie dict feched by dirver.get_cookies()
    '''

    self.__driver.delete_all_cookies()
    for entity in entities:
      if 'expiry' in entity:
        entity['expiry'] = int(entity['expiry'])

      self.__driver.add_cookie(entity)


  def set(self,cookies):
    '''
    Add cookies to the current browsing context
    Parameter:
      cookies : a string or dict cookies' key and value 
       - 'BIDUPSID=77884ECAEE62BDD2A4A723BEF544DCB2; PSTM=1715957318'
       - {'BIDUPSID':'77884ECAEE62BDD2A4A723BEF544DCB2', 'PSTM':'1715957318'}
    Returns:
      {int} : The number of successful additions
    '''
    if not cookies:
      return None

    if type(cookies) == str:
      entities = self.__get_entity_form_string(cookies)
      return self.add(entities)
    elif type(cookies) == dict:
      entities = self.__get_entity_form_dict(cookies)
      return self.add(entities)
    else:
      return 0

  def __get_complete_entity(self,entity):
    '''
    Get the cookie complete parameter dict
    Parameter:
      entity {dict} : the cookie dict
    Returns:
      {dict} : the complete cookie entity
    '''
    default_entity = self.__get_default_entity()
    # copy the input dict
    input_entity = dict(entity)
    # make sure the value is str type
    input_entity['value'] = str(input_entity['value'])

    default_entity.update(input_entity)    
    return default_entity

  def __get_entity_form_dict(self,cookies_dict):
    '''
    Convert the cookies string to the entity list
    Parameter:
      cookies_dict {dict} : A dict containing multiple cookie keys and values, such as:
        - {'BIDUPSID':'77884ECAEE62BDD2A4A723BEF544DCB2', 'PSTM':'1715957318'}
    Returns:
      {list<dict>} : the cookie entity list
    '''
    entities = []
    for name,value in cookies_dict.items():
      entities.append({
        'name':name,
        'value':value,
      })

    return entities

  def __get_entity_form_string(self,cookies_string):
    '''
    Convert the cookies string to the entity list
    Parameter:
      cookies_string {str} : A string containing multiple cookie keys and values, such as:
        - 'BIDUPSID=77884ECAEE62BDD2A4A723BEF544DCB2; PSTM=1715957318'
    Returns:
      {list<dict>} : the cookie entity list
    '''

    entities = []
    kv_list = cookies_string.split(';')
    for k_v in kv_list:
      if not k_v:
        continue
      kv=k_v.split('=')
      # must be key=value string
      if len(kv)<2:
        continue
      name = kv[0].strip()
      value = kv[1].strip()
      entities.append({
        'name':name,
        'value':value,
      })

    return entities
  
  def remove(self,name=''):
    '''
    @description 删除cookie
    @param {string} name cookie name
    '''
    if name:
      return self.__driver.delete_cookie(name)
    else:
      return self.clear()
  
  def clear(self):
    return self.__driver.delete_all_cookies()

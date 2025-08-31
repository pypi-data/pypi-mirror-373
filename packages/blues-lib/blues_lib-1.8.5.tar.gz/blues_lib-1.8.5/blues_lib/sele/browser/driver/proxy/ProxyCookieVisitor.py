import sys,os,re
from .ProxyVisitor import ProxyVisitor
from .ProxyMessageVisitor import ProxyMessageVisitor

from .filter.CookieFilter import CookieFilter
from .filter.CountFilter import CountFilter 
from .filter.URLFilter import URLFilter  

class ProxyCookieVisitor(ProxyVisitor):

  def __init__(self,cookie_config=None):
    '''
    Parameter:
      cookie_config {dict} : the cookie's filter pattern
      {
        'url_pattern': 'abc/efg', # the request url regexp pattern
        'value_pattern': 'a=b', # the cookie value's regexp pattern
      }
    '''
    self.__cookie_config = cookie_config if cookie_config else {}

  def visit(self,proxy_message,):
    messages = proxy_message.accept_message_visitor(ProxyMessageVisitor())
    if not messages:
      return ''
    
    filter_messages = self.__filter(messages)
    if not filter_messages:
      return ''

    request = filter_messages[0]['request']
    return request['cookie']
    

  def __filter(self,messages):
    count = 1
    filter_chains = URLFilter(self.__cookie_config.get('url_pattern'))
    filter_chains.set_next(CookieFilter(self.__cookie_config.get('value_pattern'))).set_next(CountFilter(count))
    return filter_chains.filter(messages)

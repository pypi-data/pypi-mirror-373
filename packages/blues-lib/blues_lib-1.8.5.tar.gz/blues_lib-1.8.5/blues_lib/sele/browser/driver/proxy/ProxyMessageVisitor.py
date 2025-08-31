from seleniumwire.utils import decode
from .ProxyVisitor import ProxyVisitor

class ProxyMessageVisitor(ProxyVisitor):

  def visit(self,proxy_message):
    '''
    @description : Return the whole http messages
    @returns {dict[] | None}
    '''
    if not proxy_message.requests:
      return None

    messages = []
    for request in proxy_message.requests:
      if not request.response:
        continue
      messages.append({
        'request':self.__get_request(request),
        'response':self.__get_response(request.response),
      })

    return messages if messages else None

  def __get_request(self,request):
    return {
      'url':request.url, 
      'path':request.path, 
      'querystring':request.querystring, 
      'method':request.method, 
      'headers':dict(request.headers), 
      'cookie':self.__get_header_cookie(request.headers),
      'params':request.params, 
      'date':request.date.isoformat(), 
      'body':str(request.body, encoding='utf-8'), 
    }

  def __get_response(self,response):
    encoding = response.headers.get('Content-encoding', 'identity')
    return {
      'status_code':response.status_code, 
      'reason':response.reason, 
      'headers':dict(response.headers), 
      'date':response.date.isoformat(), 
      'body':decode(response.body, encoding),
    }
  
  def __get_header_cookie(self,headers):
    if headers.get('cookie'):
      return headers.get('cookie')
    if headers.get('Cookie'):
      return headers.get('Cookie')
    if headers.get('COOKIE'):
      return headers.get('COOKIE')
    return ''


  
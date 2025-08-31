class ProxyMessage():

  def __init__(self,requests):
    self.requests = requests

  def accept_message_visitor(self,message_visitor):
    '''
    @description : get all http messages
    @param {ProxyMessageVisitor} message_visitor
    @returns {list<dict>}
    '''
    return message_visitor.visit(self)
  
  def accept_cookie_visitor(self,cookie_visitor):
    '''
    @description : get a cookie dict
    @param {ProxyCookieVisitor} cookie_visitor
    @returns {dict}
    '''
    return cookie_visitor.visit(self)

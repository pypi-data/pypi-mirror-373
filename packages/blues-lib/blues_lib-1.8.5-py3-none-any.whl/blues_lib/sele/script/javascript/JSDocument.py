from selenium.webdriver.remote.webelement import WebElement
class JSDocument():

  # == module 1: html or text == #
  def html(self,selector,html=None,parent_selector=''):
    '''
    @description : get or set html
    @param {str} selector css选择器
    @param {str} html 写入文本或HTML
    @returns {str|None} return dom html when as getter
    '''
    if html==None:
      if parent_selector and type(parent_selector)==str:
        script = 'return document.querySelector(`%s %s`).innerHTML;' % (parent_selector,selector)
      elif isinstance(parent_selector, WebElement):
        script = 'return arguments[0].querySelector(`%s`).innerHTML;' % (selector)
      else:
        script = 'return document.querySelector(`%s`).innerHTML;' % (selector)
    else:
      if parent_selector and type(parent_selector)==str:
        script = 'document.querySelector(`%s %s`).innerHTML=`%s`;' % (parent_selector,selector,html)
      elif isinstance(parent_selector, WebElement):
        script = 'return arguments[0].querySelector(`%s`).innerHTML=`%s`;' % (selector,html)
      else:
        script = 'document.querySelector(`%s`).innerHTML=`%s`;' % (selector,html)
    return self.execute(script,parent_selector)
  
  def replace(self,selector,html=''):
    # remove all
    script = '''
      var web_elements = document.querySelectorAll(`%s`);
      var cal_count = 0;
      if(web_elements.length){
        for(var i=0; i<web_elements.length;i++){
          web_element = web_elements[i];
          cal_count+=1;
          web_element.outerHTML=`%s`;
        }
      }
      return cal_count;
    ''' % (selector,html)
    return self.execute(script)
  
  def text(self,selector,text=None,parent_selector=''):
    '''
    @description : get or set text
    @param {str} selector css选择器
    @param {str} text 
    @returns {str|None} return dom html when as getter
    '''
    if text==None:
      if parent_selector and type(parent_selector)==str:
        script = 'return document.querySelector(`%s %s`).innerText;' % (parent_selector,selector)
      elif isinstance(parent_selector, WebElement):
        script = 'return arguments[0].querySelector(`%s`).innerText;' % (selector)
      else:
        script = 'return document.querySelector(`%s`).innerText;' % (selector)
    else:
      if parent_selector and type(parent_selector)==str:
        script = 'document.querySelector(`%s %s`).innerText=`%s`;' % (parent_selector,selector,text)
      elif isinstance(parent_selector, WebElement):
        script = 'return arguments[0].querySelector(`%s`).innerText=`%s`;' % (selector,text)
      else:
        script = 'document.querySelector(`%s`).innerText=`%s`;' % (selector,text)
    return self.execute(script,parent_selector)

  def html_after(self,selector,html=''):
    '''
    @description PM04 追加元素内容
    @param {str} selector css选择器
    @param {str} html 写入文本或HTML
    '''
    script = '''
      var ele = document.querySelector(`%s`); 
      var html = ele.innerHTML;
      ele.innerHTML=html+`%s`;
    ''' % (selector,html)
    return self.execute(script)

  def text_after(self,selector,text):
    '''
    @description : append text 
    @param {str} selector css选择器
    @param {str} text 
    '''
    script = '''
      var ele = document.querySelector(`%s`); 
      var text = ele.innerText;
      ele.innerText=text+`%s`;
    ''' % (selector,text)
    return self.execute(script)

  # == module 2: remove and empty == #
  def remove(self,selector):
    '''
    @description : remove the html dom
    @param {str} selector : css selector
    '''
    return self.replace(selector,'')

  def empty(self,selector):
    '''
    @description : remove the html dom
    @param {str} selector : css selector
    '''
    return self.html(selector,'')

  # == module 3: value == #
  def write(self,selector,value=''):
    '''
    @description : set form element's valu
    '''
    script = '''
      document.querySelector(`%s`).value=`%s`;
    ''' % (selector,value)
    return self.execute(script)

  
  def write_after(self,selector,value=''):
    '''
    @description : set form controller's value
    '''
    script = '''
      var ele = document.querySelector(`%s`); 
      var value = ele.value;
      ele.value=value+`%s`;
    ''' % (selector,value)
    self.execute(script)

  def write_para(self,selector,texts,LF_count=1):
    '''
    Write paras to textarea
    '''
    value = ''
    if texts:
      for text in texts:
        value+=text+('\n'*LF_count)

    return self.write(selector,value)

  # == module 4: attr and css == #
  def attr(self,selector,key_or_attrs):
    '''
    @description : get or set element's attribute
    @param {str} selector : element's css selector
    @param {str|dict} key_or_attrs  
    @returns {str|None} : return the attr's value in gtter
    '''
    if type(key_or_attrs)==str:
      script = 'return document.querySelector(`%s`).getAttribute(`%s`);' % (selector,key_or_attrs)
      return self.execute(script)
    else:
      for key,value in key_or_attrs.items():
        script = 'document.querySelector(`%s`).setAttribute(`%s`,`%s`);' % (selector,key,value)
        self.execute(script)
   
  def css(self,selector,key_or_attrs,parent_selector=''):
    '''
    @description : get or set element's style
    @param {str} selector : element's css selector
    @param {str|dict} key_or_attrs  
    @returns {str|None} : return the css style's value in gtter
    '''
    if type(key_or_attrs)==str:
      if parent_selector and type(parent_selector)==str:
        script = 'return document.querySelector(`%s %s`).style[`%s`];' % (parent_selector,selector,key_or_attrs)
      elif isinstance(parent_selector, WebElement):
        script = 'return arguments[0].querySelector(`%s`).style[`%s`];' % (selector,key_or_attrs)
      else:
        script = 'return document.querySelector(`%s`).style[`%s`];' % (selector,key_or_attrs)
      return self.execute(script,parent_selector)
    else:
      for key,value in key_or_attrs.items():
        if parent_selector and type(parent_selector)==str:
          script = 'document.querySelector(`%s %s`).style[`%s`]=`%s`;' % (parent_selector,selector,key,value)
        elif isinstance(parent_selector, WebElement):
          script = 'arguments[0].querySelector(`%s`).style[`%s`]=`%s`;' % (selector,key,value)
        else:
          script = 'document.querySelector(`%s`).style[`%s`]=`%s`;' % (selector,key,value)
          print('-->script',script)
        self.execute(script,parent_selector)
  
  # == module 5: size and positon == #
  def get_window_size(self):
    script = 'return {width:window.innerWidth,height:window.innerHeight};'
    return self.execute(script)

  def get_document_size(self):
    script = 'return {width:document.documentElement.offsetWidth,height:document.documentElement.offsetHeight};'
    return self.execute(script)

  def get_size(self,selector):
    script = 'var ele=document.querySelector(`%s`); return {width:ele.offsetWidth,height:ele.offsetHeight};' % selector
    return self.execute(script)
  
  # == module 6: alert and frame == #
  def alert(self,*args):
    '''
    @description : alert
    @param {tuple} args : one or more string 
    '''
    script = '''
    var alert_str = '';
    if(arguments.length>0){
      for(var i=0;i<arguments.length;i++){
        alert_str+=' '+arguments[i];
      }
    }
    return alert(alert_str);
    '''
    self.execute(script,*args)

  # == module 7: specific setting == #
  def highlight(self,selector):
    if not selector:
      return
    script = '''
      document.querySelector(`%s`).style.border="1px solid red";
    ''' % selector
    return self.execute(script)


  # == module 8: append elements == #
  def append(self,slot_selector,html):
    self.__insert_node(slot_selector,html,method="append")
  
  def prepend(self,slot_selector,html):
    self.__insert_node(slot_selector,html,method="prepend")

  def __insert_node(self,slot_selector,html,method="append"):
    '''
    use the createRange (not createElement) to avoid to add a middle div element
    '''
    script = '''
      var newElement = document.createRange().createContextualFragment(`%s`);
      document.querySelector(`%s`).%s(newElement);
    ''' % (html,slot_selector,method)
    return self.execute(script)

  # == module 9: exists == #
  def exists(self,selector):
    script = '''
    return document.querySelector(`%s`);
    ''' % selector
    return self.execute(script)


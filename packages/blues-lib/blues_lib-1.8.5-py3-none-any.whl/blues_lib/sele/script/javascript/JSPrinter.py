class JSPrinter():
  
  BAR_ID = 'blues-info-bar'
  BAR_SLOT = 'body'
  BAR_HEIGHT = '50px'
  COLOR = {
    'success':'rgb(25,135,84)',
    'info':'rgb(13,202,240)', # 13,110,253
    'warning':'rgb(255,193,7)',
    'error':'rgb(220,53,69)',
    'plain':'rgb(255,255,255)',
  }
  
  def print_success(self,text=''):
    self.print(text,'success')
  
  def print_info(self,text=''):
    self.print(text,'info')

  def print_warning(self,text=''):
    self.print(text,'warning')

  def print_error(self,text=''):
    self.print(text,'error')

  def print(self,text='',color='plain'):
    if not text:
      return
    if not self.exists('#'+self.BAR_ID):
      self.__set_bar()
    self.__write(text,color)

  def __write(self,text,color):
    html = '<p style="line-height:22px;margin:0;font-size:14px;color:%s;">%s</p>' % (self.COLOR[color],text)
    self.prepend('#'+self.BAR_ID,str(html))
    
  def __set_bar(self):
    html = '<div id="'+self.BAR_ID+'" style="width:94%;padding:3px 3%;z-index:1000;height:'+self.BAR_HEIGHT+';overflow:auto;background:black;color:white;position:fixed;top:0;left:0;"></div>'
    self.prepend(self.BAR_SLOT,html)
    self.css(self.BAR_SLOT,{
      'paddingTop':self.BAR_HEIGHT,
    })


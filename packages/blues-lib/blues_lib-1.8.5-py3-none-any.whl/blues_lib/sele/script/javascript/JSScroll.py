class JSScroll():
  
  # == module 1 : scroll x and y == #
  def scroll_x(self,left):
    '''
    @description : scroll along the X-axis
    @param {int} left : the offset tos selector's left border
    '''
    script = "window.scrollTo(%s,0);" % left
    return self.execute(script)
  
  def scroll_y(self,top):
    '''
    @description : scroll along the X-axis
    @param {int} top : the offset tos selector's left border
    '''
    script = "window.scrollTo(0,%s);" % top
    return self.execute(script)

  def scroll_bottom(self):
    '''
    @description : scroll the document to bottom
    '''
    size = self.get_document_size()
    self.scroll_y(size['height'])

  def scroll_top(self):
    '''
    @description : scroll the document to top
    '''
    self.scroll_y(0)
  
  def lazy_scroll_bottom(self,step=500,interval=1000,max_step=-1):
    '''
    @description : scroll the page to the bottom, support the content was loaded lazy
    @param {int} step : the scroll height one time
    @param {int} interval : the wait time afater scroll
    @param {int} max_step : the max sroll times, -1 means scrolling to the bottom
    '''
    js_script='''
    // 最后一个参数是python程序自动传入的回调
    var callback = arguments[arguments.length-1];
    (function(){
      var scrollHeight = document.body.scrollTop; // 当前滚动条位置
      var step = %s;
      var interval = %s;
      var maxStep = %s;
      var scrolledCount = 0;
      function scroll(){
        // 没有超过设置的最大次数，且与最新内容高度比较没有到底，继续执行
        var unreachedBottom = scrollHeight<document.body.scrollHeight-window.innerHeight;
        var shouldContinue = (maxStep==-1 || scrolledCount<maxStep);
        if(shouldContinue && unreachedBottom){
          scrolledCount++;
          scrollHeight += step;
          window.scroll(0,scrollHeight);
          document.title = scrollHeight;
          setTimeout(scroll,interval);
        }else{
          // 必须显式回调结束程序，否则程序会超时异常
          callback(scrollHeight);
        }
      }
      // 使用setTimeout程序是必须用异步函数，否则浏览器不会等待程序执行完毕就关闭
      setTimeout(scroll,interval);
    })();
    ''' % (step,interval,max_step)
    # 返回值是callback抛出值
    return self.execute_async(js_script)

  # == module 2 : scroll element to window == #
  def scroll_to_view(self,selector):
    script = 'document.querySelector(`%s`).scrollIntoView(true);' % selector
    self.execute(script)

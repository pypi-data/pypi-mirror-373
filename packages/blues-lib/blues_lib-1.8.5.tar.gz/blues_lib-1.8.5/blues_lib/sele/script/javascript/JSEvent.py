class JSEvent():

  def click(self,selector,parent_selector=''):
    sel = selector
    if parent_selector:
      sel = '%s %s' % (parent_selector,selector)
    script = 'document.querySelector("%s").click();' % sel
    self.execute(script)

  

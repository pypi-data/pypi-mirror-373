class JSAlert():

  # == module 1: html or text == #
  def alert(self,text='accept'):
    '''
    Popup the alert dialog
    Parameter:
      text {str} : the alert's text 
    Returns:
      {None} : alert return undefined in js
    '''
    script = '''
      return alert(`%s`);
    ''' % (text)
    return self.execute(script)
  

  def confirm(self,text='accept or dismiss'):
    '''
    Returns:
      {bool} : accept - true; dismiss - false
    '''
    script = '''
      return confirm(`%s`);
    ''' % (text)
    return self.execute(script)
  
  def prompt(self,text='input and confirm'):
    '''
    Returns:
      {str|None} : accept - the input value; dismiss - None
    '''
    script = '''
      return prompt(`%s`);
    ''' % (text)
    return self.execute(script)
  

class JSJQuery():

  def is_jquery_available(self):
    return self.is_var_available('jQuery')
    
  def load_jquery(self):
    cdn = 'https://libs.baidu.com/jquery/2.0.0/jquery.min.js'
    self.load_script(cdn)

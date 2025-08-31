from .javascript.JavaScript import JavaScript

class Script():

  def __init__(self,driver):
    self.javascript = JavaScript(driver)

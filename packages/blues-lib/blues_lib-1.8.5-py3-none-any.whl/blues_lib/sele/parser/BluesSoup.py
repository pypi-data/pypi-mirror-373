from bs4 import BeautifulSoup

class BluesSoup():
  
  def __init__(self,driver):
    self.driver = driver
    self.soup = None

  def next(self):
    '''
    @description : get the current page soup
    '''
    html = self.driver.page_source
    self.soup = BeautifulSoup(html,'lxml')

  def find(self,name):
    if not self.soup:
      self.next()
    return self.soup.find(name)
  
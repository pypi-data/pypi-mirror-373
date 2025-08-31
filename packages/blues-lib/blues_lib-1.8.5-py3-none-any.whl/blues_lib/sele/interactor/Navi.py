from .Alert import Alert

class Navi():
 
  def __init__(self,driver):
    self.__driver = driver
    self.__alert = Alert(driver)
      
  def open(self,url):
    '''
    Open a page
    '''
    if self.is_available():
      self.__driver.get(url)
      
  def get(self,url):
    self.open(url)

  def close(self):
    '''
    Close the current window or tab
    If only one window/tab ,the browser will be closed
    '''
    self.__alert.accept()
    if self.is_available():
      self.__driver.close()

  def is_available(self):
    '''
    Whether the current driver is available
    Returns:
      {bool}
    '''
    try:
      self.__driver.current_url
      return True
    except Exception as e:
      return False

  def quit(self):
    '''
    Close all windows and tabs
    Close the browser process
    Close the driver's process
    '''
    self.__alert.accept()
    if self.is_available():
      self.__driver.quit()

  def back(self):
    '''
    Back to the prev page
    '''
    if self.is_available():
      self.__driver.back()
  
  def forward(self):
    '''
    Forward to the next page
    '''
    if self.is_available():
      self.__driver.forward()

  def refresh(self):
    '''
    Refresh to the current page
    '''
    if self.is_available():
      self.__driver.refresh()
  

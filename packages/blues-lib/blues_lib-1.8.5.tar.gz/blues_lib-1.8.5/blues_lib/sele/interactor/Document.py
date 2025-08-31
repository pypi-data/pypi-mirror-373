class Document():
 
  def __init__(self,driver):
    self.__driver = driver

  def get_title(self):
    # Return the document's title
    return self.__driver.title
  
  def get_name(self):
    # Return the document's name
    return self.__driver.name
  
  def get_url(self):
    # Return the document's url
    return self.__driver.current_url
  
  def get_source(self):
    # Return the document's page source
    return self.__driver.page_source
  
  def set_page_timeout(self,timeout:int=20):
    # Set the page load timeout
    self.__driver.set_page_load_timeout(timeout)
    
  def set_script_timeout(self,timeout:int=20):
    # Set the script timeout
    self.__driver.set_script_timeout(timeout)
    
  def set_implicitly_wait(self,timeout:int=20):
    # Set the implicitly wait
    self.__driver.implicitly_wait(timeout)



  

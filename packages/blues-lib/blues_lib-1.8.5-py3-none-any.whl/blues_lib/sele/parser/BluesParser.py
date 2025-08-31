from .BluesSoup import BluesSoup              

class BluesParser():

  def __init__(self,driver):
    self.soup= BluesSoup(driver)
import sys,os,re
from .deco.SwitchDeco import SwitchDeco
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from sele.waiter.EC import EC

# Provides methods for handling three pop-ups
class Alert():
 
  def __init__(self,driver):
    self.__driver = driver
    self.__ec = EC(driver)

  @SwitchDeco('Alert','switch_to')
  def switch_to(self):
    '''
    Switch the driver's focus to the alert window
    Returns:
      {WebElement} : the alert element 
    '''

    # Check that the pop-up exists
    if self.__ec.alert_to_be_presence(1):
      return self.__driver.switch_to.alert
    else:
      return None

  @SwitchDeco('Alert','accept')
  def accept(self,text=''):
    '''
    Accept and close the dialog
    The driver will back to main window automatically
    Returns:
      {str} the alert's text
    '''
    alert = self.switch_to()
    if not alert:
      return False
    try:
      if text:
        # not work on chrome
        alert.send_keys(text)
      alert.accept()
      return True
    except:
      return False
      
  @SwitchDeco('Alert','dismiss')
  def dismiss(self):
    '''
    Dismiss and close the dialog
    The driver will back to main window automatically
    Returns:
      {str} the alert's text
    '''
    alert = self.switch_to()
    if not alert:
      return False
    try:
      alert.dismiss()
      return True
    except:
      return False


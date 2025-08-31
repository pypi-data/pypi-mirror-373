from .Mouse import Mouse
from .Dragger import Dragger
from .Keyboard import Keyboard
from .Wheel import Wheel

class Action():

  def __init__(self,driver):
    self.mouse = Mouse(driver)
    self.dragger = Dragger(driver)
    self.keyboard = Keyboard(driver)
    self.wheel = Wheel(driver)

from .Navi import Navi
from .Alert import Alert
from .Frame import Frame
from .Cookie import Cookie
from .Document import Document
from .Window import Window

class Interactor():

  def __init__(self,driver):
    self.navi = Navi(driver)
    self.alert = Alert(driver)
    self.frame = Frame(driver)
    self.cookie = Cookie(driver)
    self.document = Document(driver)
    self.window = Window(driver)

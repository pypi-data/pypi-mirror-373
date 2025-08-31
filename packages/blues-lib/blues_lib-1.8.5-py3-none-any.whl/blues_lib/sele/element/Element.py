from .Finder import Finder
from .XPathFinder import XPathFinder

from .Info import Info
from .State import State
from .Select import Select
from .Choice import Choice
from .File import File
from .Image import Image
from .Shot import Shot
from .Input import Input
from .Popup import Popup

class Element():

  def __init__(self,driver):
    self.finder = Finder(driver)
    self.xpath_finder = XPathFinder(driver)
    self.info = Info(driver)
    self.state = State(driver)
    self.select = Select(driver)
    self.choice = Choice(driver)
    self.file = File(driver)
    self.image = Image(driver)
    self.shot = Shot(driver)
    self.input = Input(driver)
    self.popup = Popup(driver)

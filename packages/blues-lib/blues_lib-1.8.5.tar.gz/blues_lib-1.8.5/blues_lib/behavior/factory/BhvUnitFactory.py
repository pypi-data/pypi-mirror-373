from typing import Any
import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.factory.Factory import Factory
from type.model.Model import Model

from behavior.unit.Row import Row
from behavior.unit.Richtext import Richtext


class BhvUnitFactory(Factory):
  def __init__(self,model:Model,browser=None):
    self._model = model
    self._browser = browser

  def create_row(self):
    return Row(self._model,self._browser)
  
  def create_richtext(self):
    return Richtext(self._model,self._browser)

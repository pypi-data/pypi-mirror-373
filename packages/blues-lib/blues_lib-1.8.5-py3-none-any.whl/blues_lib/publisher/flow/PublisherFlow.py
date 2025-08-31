import sys,os,re
from .command.InputCMD import InputCMD
from .command.SchemaCMD import SchemaCMD
from .command.MaterialCMD import MaterialCMD
from .command.ModelCMD import ModelCMD
from .command.BrowserCMD import BrowserCMD
from .command.PublisherCMD import PublisherCMD
from .command.PersisterCMD import PersisterCMD

sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.executor.CommandFlow import CommandFlow

class PublisherFlow(CommandFlow):
  
  def load(self):
    input_cmd = InputCMD(self._context)
    schema_cmd = SchemaCMD(self._context)
    material_cmd = MaterialCMD(self._context)
    model_cmd = ModelCMD(self._context)
    browser_cmd = BrowserCMD(self._context)
    publisher_cmd = PublisherCMD(self._context)
    persister_cmd = PersisterCMD(self._context)

    # check if the input is legal
    self.add(input_cmd)

    # add context.loginer_schema  context.publisher_schema
    self.add(schema_cmd)
    
    # add context.material
    self.add(material_cmd)

    # replace the context_schema
    self.add(model_cmd)
    
    # add the context.browser
    self.add(browser_cmd)
    
    # preview and publish
    self.add(publisher_cmd)

    # update status
    self.add(persister_cmd)

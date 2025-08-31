import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.executor.CommandFlow import CommandFlow
from reporter.controller.command.NotifierCMD import NotifierCMD

class ReporterFlow(CommandFlow):
  
  def load(self):

    notifier_cmd = NotifierCMD(self._context)
    self.add(notifier_cmd)
  





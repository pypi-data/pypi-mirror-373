import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from command.NodeCommand import NodeCommand
from namespace.CommandName import CommandName
from type.output.STDOut import STDOut
from type.exception.FlowBlockedException import FlowBlockedException

class Printer(NodeCommand):

  NAME = CommandName.Control.PRINTER

  def _invoke(self)->STDOut:
    commands:str = self._summary.get('commands')
    if not commands:
      return STDOut(200,'No commands to print')
    
    for command in commands:
      output:STDOut = self._context.get(command)
      print(f'{command}: {output}')
      
    return STDOut(200,'Print done')


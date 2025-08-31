import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from command.NodeCommand import NodeCommand
from namespace.CommandName import CommandName
from type.output.STDOut import STDOut
from type.exception.FlowBlockedException import FlowBlockedException

class Blocker(NodeCommand):

  NAME = CommandName.Control.BLOCKER

  def _invoke(self)->STDOut:
    block_code:int = self._summary.get('code',200)
    block_message:str = self._summary.get('message','')
    block_script:str = self._summary.get('script','') # define a python script
    if self._output and self._output.code == block_code:
      self._clean()
      raise FlowBlockedException(f'[{self.NAME}] Block by code {block_code} - {block_message}')
    else:
      return STDOut(200,'Skip the blocker')
      
  def _clean(self)->None:
    creator_output:STDOut = self._context.get(CommandName.Browser.CREATOR.value)
    if browser := creator_output.data if creator_output else None:
      browser.quit()
 
import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from command.NodeCommand import NodeCommand
from namespace.CommandName import CommandName
from type.output.STDOut import STDOut
from type.exception.FlowBlockedException import FlowBlockedException

class Retryer(NodeCommand):

  NAME = CommandName.Control.RETRYER

  def _invoke(self)->STDOut:
    retry_code:int = self._summary.get('code',200)
    retry_message:str = self._summary.get('message','')
    if self._output and self._output.code == retry_code:
      self._clean()
      raise FlowRetryException(f'[{self.NAME}] Retry by code {retry_code} - {retry_message}')
    else:
      return STDOut(200,'Skip the retryer')
      
  def _clean(self)->None:
    creator_output:STDOut = self._context.get(CommandName.Browser.CREATOR.value)
    if browser := creator_output.data if creator_output else None:
      browser.quit()
 
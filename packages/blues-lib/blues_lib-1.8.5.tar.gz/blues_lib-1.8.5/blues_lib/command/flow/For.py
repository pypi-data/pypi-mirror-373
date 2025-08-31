import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.output.STDOut import STDOut
from command.NodeCommand import NodeCommand
from namespace.CommandName import CommandName

class Queue(NodeCommand):

  NAME = CommandName.Flow.QUEUE
  TYPE = CommandName.Type.SETTER
  

  def _invoke(self):
    # lazy to import to avoid circular import
    from flow.FlowFactory import FlowFactory
    prev_output:STDOut = None

    for context in self._node_input:
      # append prev output to current flow
      if prev_output:
        context[CommandName.IO.OUTPUT.value] = prev_output

      flow = FlowFactory(context).create()
      stdout:STDOut = flow.execute()

      if stdout.code == 200:
        self._infos.append(stdout.message)
      else:
        self._errors.append(stdout.message)

      # even the prev flow failed, we should continue
      prev_output = context[CommandName.IO.OUTPUT.value]
      
    # output the last sub flow's stdout
    self._code = prev_output.code
    self._data = prev_output.data
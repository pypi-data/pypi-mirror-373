import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.output.STDOut import STDOut
from command.NodeCommand import NodeCommand
from namespace.CommandName import CommandName

class Engine(NodeCommand):

  NAME = CommandName.Flow.ENGINE
  TYPE = CommandName.Type.SETTER
  

  def _invoke(self)->STDOut:
    # lazy to import to avoid circular import
    from flow.FlowFactory import FlowFactory
    
    queue_maps:list[dict] = self._node_input
    sub_flow = FlowFactory(queue_maps).create()
    # set the main flow output as the sub flow's init context
    if main_output:=self._context.get(CommandName.IO.OUTPUT.value):
      sub_flow.context[CommandName.IO.OUTPUT.value] = main_output

    sub_output:STDOut = sub_flow.execute()
    # set the sub flow's output as the main flow's node output
    sub_data = sub_flow.context[CommandName.IO.OUTPUT.value].data
    return STDOut(sub_output.code,sub_output.message,sub_data)

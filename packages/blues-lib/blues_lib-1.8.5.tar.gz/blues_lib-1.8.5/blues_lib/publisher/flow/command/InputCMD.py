import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.executor.Command import Command

class InputCMD(Command):

  name = __name__

  def execute(self):

    input = self._context.get('publisher')
    if not input:
      raise Exception('[AI] The param publisher is missing!')

    stereotype = input.get('stereotype')
    if not stereotype:
      raise Exception('[AI] The param publisher.stereotype is missing!')

    executor_stereotype = stereotype.get('executor')
    if not executor_stereotype:
      raise Exception('[AI] The param publisher.stereotype.executor is missing!')

    loginer_stereotype = stereotype.get('loginer')
    if not loginer_stereotype:
      raise Exception('[AI] The param publisher.stereotype.loginer is missing!')
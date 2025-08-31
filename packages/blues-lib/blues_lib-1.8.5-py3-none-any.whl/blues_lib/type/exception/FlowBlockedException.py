class FlowBlockedException(Exception):
  """自定义异常：表示流程被正常阻断（非错误，无需报错）"""
  def __init__(self, message="流程已按条件阻断，无需继续执行"):
    self.message = message
    super().__init__(self.message)
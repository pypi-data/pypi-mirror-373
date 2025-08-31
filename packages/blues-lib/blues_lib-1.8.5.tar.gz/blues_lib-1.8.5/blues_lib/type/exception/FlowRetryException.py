class FlowRetryException(Exception):
  """自定义异常：表示流程需要重试"""
  def __init__(self, message="流程需要重试"):
    self.message = message
    super().__init__(self.message)
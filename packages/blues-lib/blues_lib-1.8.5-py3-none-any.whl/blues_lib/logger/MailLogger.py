import os,sys,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from util.BluesMailer import BluesMailer
from logger.FileLogger import FileLogger

class MailLogger(FileLogger):

  def info(self,message:str,payload:dict):
    '''
    @description write log
    @param {MailPayload}
    '''
    super().info(message)
    BluesMailer.send(payload)

  def warning(self,message:str,payload:dict):
    '''
    @description write log
    @param {MailPayload}
    '''
    super().warning(message)
    BluesMailer.send(payload)
  
  def error(self,message:str,payload:dict):
    '''
    @description write log
    @param {MailPayload}
    '''
    super().error(message)
    BluesMailer.send(payload)

  def debug(self,message:str,payload:dict):
    super().debug(message)
    BluesMailer.send(payload)
    
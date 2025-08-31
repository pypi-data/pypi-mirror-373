import os

class Process:
  
  @classmethod
  def taskkill(cls,task_name):
    '''
    Stop a app's all process
    @param {str} task_name : the app's exe file name
    @returns {int} : 0-success >0- failure
    '''
    return os.system('taskkill /F /iM %s.exe' % task_name)

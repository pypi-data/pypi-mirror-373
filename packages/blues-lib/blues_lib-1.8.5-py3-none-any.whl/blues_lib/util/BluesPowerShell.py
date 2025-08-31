import subprocess
from .BluesConsole import BluesConsole

class BluesPowerShell():

  @classmethod
  def execute(cls,script):
    '''
    @description : execute ps script
    @param {str} script str or ps1 file
    @returns {dict} PSResult
    '''
    ps_script = 'powershell.exe %s' % script
    p = subprocess.Popen(ps_script,stdout=subprocess.PIPE,stderr=None)
    output,error = p.communicate()
    try:
      return {
        'code':200,
        'message':'success',
        'output':output.decode('utf-8').strip()
      }
    except:
      return {
        'code':500,
        'message':error,
        'output':output
      }

  @classmethod
  def stop_process(cls,name):
    ps_script = 'Get-Process -Name %s -ErrorAction SilentlyContinue | Stop-Process -Force' % name
    return cls.execute(ps_script)

  @classmethod
  def start_process(cls,file_path,args):
    '''
    @description : start a process, the file path and args must be warppered by single quotes
    @param {str} file_path : the absolute path of the start file (.exe)
    @param {str}  args : the multi exe executor's arguments, split by space
     - '--arg1 --arg2 --arg3'
    '''
    args_list = ''
    if args:
      args_list = '-ArgumentList \'%s\''  % args
    ps_script = 'Start-Process -FilePath \'%s\' %s' % (file_path,args_list)
    BluesConsole.info(ps_script,'Powershell: ')
    return cls.execute(ps_script )

  @classmethod
  def get_env_value(cls,name):
    '''
    @description : get env variable's value
    @param {str} name : varibale's name
    @returns {str} : return var's value or ''
    '''
    ps_script = "[Environment]::GetEnvironmentVariable('%s','machine')" % name
    result = cls.execute(ps_script)
    if result['code'] == 200:
      return result['output']
    else:
      return ''
import psutil
from .Browser import Browser
from .driver.DebugDriverCreator import DebugDriverCreator  

class BluesDebugChrome(Browser):

  def __init__(self,
      debug_config={}, # {dict} create or connect debug config : config.type {'create'|'connect'}
      std_args=None, # {dict} standard args
      exp_args=None, # {dict} experimentalargs
      cdp_args=None, # {dict} chrome devtools protocal args
      sel_args=None, # {dict} selenium args
      ext_args=None, # {dict} extension args
      executable_path=None # {str} driver.exe path: 'env' - using the env; 'xxx' - the local path; None - using the driver manager
    ):
    creator = DebugDriverCreator(
      std_args,
      exp_args,
      cdp_args,
      sel_args,
      ext_args,
      executable_path
    )

    ip = debug_config.get('ip','127.0.0.1')
    port = debug_config.get('port')
    
    if ip and port and self.__exists(ip,port):
      driver = creator.connect(debug_config)
    else:
      driver = creator.create(debug_config)

    super().__init__(driver)
    
  def __exists(self,target_ip, target_port):
    pids = []
    for conn in psutil.net_connections(kind='inet'):
      if (
        conn.status == 'LISTEN'
        and conn.laddr.ip == target_ip
        and conn.laddr.port == target_port
      ):
        try:
          process = psutil.Process(conn.pid)
          if "chrome" in process.name().lower():
            pids.append(conn.pid)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
          continue
    return pids
    
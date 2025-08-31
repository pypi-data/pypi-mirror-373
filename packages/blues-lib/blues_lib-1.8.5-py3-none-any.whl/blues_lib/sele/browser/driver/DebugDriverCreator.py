from .DriverCreator import DriverCreator

class DebugDriverCreator(DriverCreator):
    
  def connect(self,config):
    '''
    connect to a existed browser driver
    set a remote ip to control the server's browser
    @pram {dict} config : 
      - {str} ip : such as 127.0.0.1 (local dirver);  47.76.221.247 (remote driver)
      - {int} port : such as 9222
    '''
    ip = config.get('ip','127.0.0.1')
    port = config.get('port')
    if ip and port:
      args = {
        'debugger_address' : '%s:%s' % (ip,port)
      }
      self._sel_args.update(args)

    return super().create()
  
  def create(self,config):
    '''
    Open a chrome base on ip and port
    @pram {dict} config : 
      - {str} ip : such as 127.0.0.1 (local); 0.0.0.0 (for every ips); 47.76.221.247 (specify ip)
      - {int} port : such as 9222
      - {str} dir : such as c:/selenium/user01
    '''
    ip = config.get('ip','127.0.0.1')
    port = config.get('port')
    datadir = config.get('dir')
    args = {}
    if ip and port:
      args = {
        'debugport':port,
        'debugaddr':ip,
      }
    if datadir:
      args['debugdir'] = datadir
    
    if args:
      self._std_args.update(args)

    return super().create()
  
import time,datetime
from .BluesConsole import BluesConsole

class BluesDateTime():

  spend = 0

  @classmethod
  def get_today(cls):
    now = datetime.datetime.now()
    return now.strftime('%Y-%m-%d')

  @classmethod
  def get_time(cls):
    now = datetime.datetime.now()
    return now.strftime('%H:%M:%S')

  @classmethod
  def get_now(cls):
    now = datetime.datetime.now()
    return now.strftime('%Y-%m-%d %H:%M:%S')

  @classmethod
  def get_timestamp(cls):
    now = datetime.datetime.now()
    return int(now.timestamp() * 1000)

  @classmethod
  def count_down(cls,payload={}):
    '''
    @description : count down
    @param {int} payload.duration  : duration seconds
    @param {int} payload.interval  : interval seconds
    @param {str} payload.title  : title
    @param {bool} payload.printable  : print in the console
    '''

    duration = int(payload.get('duration',10))
    interval = int(payload.get('interval',1))
    title = payload.get('title','coutdown')
    printable = payload.get('printable',True)

    if not duration:
      return

    if interval <=0:
      interval =1
    
    if printable: 
      BluesConsole.wait('%s : %s' % (title,duration-cls.spend))

    time.sleep(interval) 
    cls.spend+=interval
    if cls.spend < duration:
      cls.count_down(payload)
    else:
      cls.spend=0

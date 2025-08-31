class BluesConsole():

  COLORS = {
    'warn' : '\033[93m',
    'success' : '\033[92m',
    'info' : '\033[94m',
    'error' : '\033[91m',
    'wait' : '\033[95m',
    'bold' : '\033[1m',
    'underline' : '\033[4m',
    'default' : '\033[0m',
  }

  @classmethod
  def get_sequence_values(cls,value):
    if type(value)!=list and type(value)!=tuple:
      return [value]
    else:
      return value

  @classmethod
  def success(cls,value,label='Sucess'):
    '''
    @description : print value with colorful prefix
    @param {any} value : any type of value
    @param {str} label :  the label in prefix
    '''
    values = BluesConsole.get_sequence_values(value)
    print(f"\n{cls.COLORS['success']}{label} >>> {cls.COLORS['default']}",*values)
  
  @classmethod
  def info(cls,value,label='Info'):
    values = BluesConsole.get_sequence_values(value)
    print(f"\n{cls.COLORS['info']}{label} >>> {cls.COLORS['default']}",*values)
  
  @classmethod
  def warn(cls,value,label='Warn'):
    values = BluesConsole.get_sequence_values(value)
    print(f"\n{cls.COLORS['warn']}{label} >>> {cls.COLORS['default']}",*values)
  
  @classmethod
  def error(cls,value,label='Error'):
    values = BluesConsole.get_sequence_values(value)
    print(f"\n{cls.COLORS['error']}{label} >>> {cls.COLORS['default']}",*values)
  
  @classmethod
  def wait(cls,value,label='Wait'):
    values = BluesConsole.get_sequence_values(value)
    print(f"\n{cls.COLORS['wait']}{label} >>> {cls.COLORS['default']}",*values)
  
  @classmethod
  def bold(cls,value,label='Bold'):
    values = BluesConsole.get_sequence_values(value)
    print(f"\n{cls.COLORS['bold']}{label} >>> {cls.COLORS['default']}",*values)
  
  @classmethod
  def underline(cls,value,label='Underline'):
    values = BluesConsole.get_sequence_values(value)
    print(f"\n{cls.COLORS['underline']}{label} >>> {cls.COLORS['default']}",*values)
  
  @classmethod
  def print(cls,value,label='Log'):
    values = BluesConsole.get_sequence_values(value)
    print(f"\n{label} >>> ",*values)


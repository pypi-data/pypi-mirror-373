import sys,os,re,time
from .Visitor import Visitor
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from util.BluesConsole import BluesConsole

class MultiVisitor(Visitor):
  '''
  Publish one material several times by select a different activity
  The form has a selection or checkbox field
  '''
  def __init__(self,schema_factory,method_count):
    '''
    Parameters:
      schema_factory { ReleaserSchemaFactory }
      method_count {dict} : the schema create method and count
       {'method1':1,'method2':2}
    '''
    super().__init__()

    self.schema_factory = schema_factory
    self.method_count = method_count

  def visit_standard(self,publisher) -> None:
    self.publisher = publisher
    self.publish()

  def visit_once_login(self,publisher) -> None:
    self.publisher = publisher
    self.publish()

  def visit_test(self,publisher,callback) -> None:
    self.publisher = publisher
    schema = self.__get_schema()
    self.publisher.set_schema(schema)
    callback(self.publisher.schema)

  def __get_schema(self,method_name=''):
    fn_name = method_name
    if not method_name:
      fn_name = list(self.method_count.keys())[0]
    method = getattr(self.schema_factory,fn_name)
    return method()

  # concreate calculate
  def publish(self):
    if not self.publisher.material:
      raise Exception('No available materials')

    self.publisher.login()
    self.release()
    self.publisher.quit()
  
  def release(self):
    # ergodic by channes
    pubed_count = 0
    for method_name,count in self.method_count.items():
      if not hasattr(self.schema_factory,method_name)  or not count:
        continue
      
      # ergodic by count
      for i in range(count):
        schema = self.__get_schema(method_name)

        if not schema.material:
          raise Exception('No more available materials')
        
        pubed_count+=1
        BluesConsole.info('Publishing the %sth material in channel: %s' % (pubed_count,method_name))
        self.publisher.set_schema(schema)
        # releae the material
        self.publisher.release()


    

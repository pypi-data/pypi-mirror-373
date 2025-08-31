import sys,os,re
from abc import ABC,abstractmethod
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.model.Model import Model
from behavior.BhvExecutor import BhvExecutor       
from material.file.MatFile import MatFile
from util.BluesURL import BluesURL
from util.BluesDateTime import BluesDateTime
from deco.LogDeco import LogDeco

class Publisher(ABC): 

  def __init__(self,browser,schema):
    '''Create a form publisher instance
    
    Args:
      {LoginChrome} browser : the logined browser
      {Schema} schema : the modeled schema
    '''
    self.browser = browser
    self.schema = schema
    self.message = ''

  @LogDeco()
  def publish(self):
    is_preview = self.schema.basic.get('preview',True)

    self._open()
    self._prepare()
    self._execute()
    self._preview()

    if not is_preview: 
      self._submit()
    
    self._clean()
    status = self._validate()
    screenshot = self._shot(status)
    self._delay()
    self._quit()
    
    self.set_message(status)
    return {
      'status':status,
      'screenshot':screenshot,
    }
    
  def set_message(self,status):
    message = 'Succeeded' if status=='pubsuccess' else 'Failed'
    self.message = message+' to publish'

  @abstractmethod
  def _execute(self):
    pass

  def _open(self):
    url = self.schema.basic.get('url')
    self.browser.open(url)

  def _prepare(self):
    if self.schema.preparation:
      model = Model(self.schema.preparation)
      executor = BhvExecutor(model,self.browser)
      executor.execute()

  def _preview(self):
    if self.schema.preview_execution:
      model = Model(self.schema.preview_execution)
      executor = BhvExecutor(model,self.browser)
      executor.execute()

  def _submit(self):
    if self.schema.submit_execution:
      model = Model(self.schema.submit_execution)
      executor = BhvExecutor(model,self.browser)
      executor.execute()

  def _clean(self):
    if self.schema.cleanup:
      model = Model(self.schema.cleanup)
      executor = BhvExecutor(model,self.browser)
      executor.execute()
      
  def _quit(self):
    if self.browser:
      self.browser.quit()

  def _validate(self):
    url = self.schema.basic.get('url')
    status = 'pubfailure'
    
    # if published successfully, the url would change
    if self.browser.waiter.ec.url_changes(url,10):
      status = 'pubsuccess'
    
    return status

  def _shot(self,status):
    site = self.schema.basic.get('site','nosite')
    dirs = [site]
    ts = BluesDateTime.get_timestamp()
    file_name = '%s_%s.png' % (status,ts)
    # 待补充此方法
    shot_dir = MatFile.get_screenshot_dir(dirs)
    file_path = BluesURL.get_file_path(shot_dir,file_name)
    return self.browser.interactor.window.screenshot(file_path)

  def _delay(self):
    BluesDateTime.count_down({
      'duration':5,
      'title':'Delay to quit'
    })

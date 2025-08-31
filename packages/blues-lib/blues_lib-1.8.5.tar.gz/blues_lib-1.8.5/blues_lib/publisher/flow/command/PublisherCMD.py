import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.executor.Command import Command
from publisher.factory.PublisherFactory import PublisherFactory   
from util.BluesDateTime import BluesDateTime

class PublisherCMD(Command):

  name = __name__

  def execute(self):
    browser = self._context['publisher'].get('browser')
    executor_schema = self._context['publisher']['schema'].get('executor')
    site = executor_schema.basic.get('site')
    mode = executor_schema.basic.get('mode')

    publisher = PublisherFactory(browser,executor_schema).create(mode)
    if not publisher:
      raise Exception('[Publisher] Failed to create a publisher!')

    result = publisher.publish()
    material = self._context['publisher']['material']
    material['material_status'] = result['status'] # pubsuccess or pubfailure
    material['material_pub_shot'] = result['screenshot'] 
    material['material_pub_date'] = BluesDateTime.get_now()
    material['material_pub_platform'] = site
    material['material_pub_channel'] = mode



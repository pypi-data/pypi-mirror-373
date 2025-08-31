import sys,os,re

from .NAPS import NAPS
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from schema.releaser.channels.ChannelsSchemaFactory import ChannelsSchemaFactory
from loginer.factory.ChannelsLoginerFactory import ChannelsLoginerFactory   
from sele.publisher.OnceLoginPublisher import OnceLoginPublisher
from sele.publisher.visitor.ActivityVisitor import ActivityVisitor

# don't need spide
class ChannelsVideoNAPS():
  '''
  1. Login the publish page
  2. Upload the video and fill the from
  3. Submit
  '''

  def publish(self):
    loginer_factory = ChannelsLoginerFactory()
    loginer = loginer_factory.create_qrcode(once=True)

    factory = ChannelsSchemaFactory()
    schema = factory.create_video()
    
    # max activity count
    maxnium = 50
    # start activity index (start from 0)
    starting_index=1
    # recursive wait time seconds ,at lease 100
    recursive_interval=60*60*2
    # recursive time , max 24
    recursive_time=12

    visitor = ActivityVisitor(maxnium,starting_index,recursive_interval,recursive_time)
    publisher = OnceLoginPublisher(schema,loginer)
    publisher.accept(visitor)


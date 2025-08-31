import os,re,sys
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from util.BluesFiler import BluesFiler  
# 还是python2语法，咱不可用，内部使用ffmpeg实现
from castro import Castro

class BluesVideoCapturer():

  capturer = None

  @classmethod
  def start(cls,file_path=''):
    if file_path:
      dl_path = file_path
    else:
      filename = BluesFiler.get_filename(extension='swf')
      dl_path = BluesFiler.get_file('video',filename)
    cls.capturer = Castro(filename=dl_path)
    cls.capturer.start()

  @classmethod
  def stop(cls):
    if cls.capturer:
      cls.capturer.stop()
      cls.capturer=None
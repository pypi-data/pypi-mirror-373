from PIL import Image
from .BluesFiler import BluesFiler

class BluesImager:

  @classmethod
  def download(cls,urls,directory,target_size=None):
    success = lambda local_image : cls.resize(local_image,target_size)
    return BluesFiler.download(urls,directory,success)

  @classmethod
  def get_wh_ratio(cls,local_image):
    '''
    Get the image's width / height ratio
    Returns {float}
    '''
    try:
      with Image.open(local_image) as im:
        size = im.size
        return round(size[0]/size[1],2)
    except Exception as e:
      return 1

  @classmethod
  def __get_scale_size(cls,current_size,target_size):
    '''
    @description : Gets the smallest scale size
    @param {tuple} current_size : current the image's real size
    @param {tuple} target_size : the target size ,the will may be not scale 
    @returns {tuple} new size
    '''
    (current_width,current_height) = current_size
    (target_width,target_height) = target_size

    if not target_size or (not target_width and not target_height):
      return current_size

    if target_width and not target_height:
      target_height = int(target_width*current_height/current_width) 

    if target_height and not target_width:
      target_width = int(target_height*current_width/current_height) 

    # get the scale min target size
    if target_width and target_height:
      width_ratio = target_width/current_width
      height_ratio = target_height/current_height
      # With a bigger scale as the standard
      if width_ratio>height_ratio:
        target_height = int(target_width*current_height/current_width) 
      else:
        target_width = int(target_height*current_width/current_height) 
    return (target_width,target_height)

  @classmethod
  def resize(cls,local_image,target_size):
    '''
    @description : set image's size
    @param {str} local_image 
    @param {tuple} target_size : (width,height)
    '''

    # 等比例设置
    with Image.open(local_image) as im:

      current_size = im.size
      scale_size = cls.__get_scale_size(current_size,target_size)

      copy_image = cls.__copy(im,local_image,'','original')
      new_image = im.resize(scale_size)

      # convert rgba to rgb; or can't save to jpeg
      rgb_image = new_image.convert('RGB')
      rgb_image.save(local_image)

      return {
        'original_image':copy_image,
        'original_size':current_size,
        'target_size':target_size,
        'size':scale_size
      }

  @classmethod
  def copy(cls,local_image,new_name='',prefix='',suffix='',separator='-'):
    with Image.open(local_image) as im:
      return cls.__copy(im,local_image,new_name,prefix,suffix,separator)

  @classmethod
  def __copy(cls,im,local_image,new_name='',prefix='',suffix='',separator='-'):
    img_copy = im.copy()
    path = BluesFiler.get_rename_file(local_image,new_name,prefix,suffix,separator)
    img_copy.save(path)
    return path



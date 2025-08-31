import re
from PIL import Image
from .BluesURL import BluesURL

class BluesImage():
  
  '''
  BaiJia news:412 * 545
  '''
  MIN_WIDTH = 650
  MIN_HEIGHT = 650
  
  @classmethod
  def convert_type(cls,image_path,image_type='JPEG'):
    '''
    Convert the image's type

    Parameter:
      image_path {str} : the local image dir path
      image_type {str} : the aim image type

    Return:
      {str} : the converted image path
        If converted failure, return empty string
    '''
    file_name = BluesURL.get_file_name(image_path)
    jpeg_pattern = r'\.jpe?g$'
    if re.search(jpeg_pattern,file_name,flags=re.IGNORECASE):
      return image_path
    else:
      new_path = BluesURL.rename_extend_name(image_path,'jpg')
      try:
        image = Image.open(image_path)
        image.convert('RGB').save(new_path, image_type)
        image.close()
        return new_path
      except Exception as e:
        return ''

  @classmethod
  def convert_size(cls,image_path,size=None):
    '''
    Convert the image's size

    Parameter:
      image_path {str} : the local image dir path
      size {tuple|list} : the aim image size ,such as [100,200] [100,] [,200]

    Return:
      {bool} : the convet status
    '''
    if size:
      return cls.resize(image_path,size)

    image = Image.open(image_path)
    width,height = image.size
    image.close()
    if width>= cls.MIN_WIDTH and height>=cls.MIN_HEIGHT:
      return 
    
    size = cls.get_min_size(width,height)
    return cls.resize(image_path,size)

  @classmethod
  def get_min_size(cls,width,height):

    new_width = width
    new_height = height

    # Make sure both the width and height large than the MIN value
    if width>= cls.MIN_WIDTH and height<cls.MIN_HEIGHT:
      new_height = cls.MIN_HEIGHT
      new_width = int(width*new_height/height) 

    if width<cls.MIN_WIDTH and height>=cls.MIN_HEIGHT:
      new_width = cls.MIN_WIDTH
      new_height = int(new_width*height/width) 

    if width<cls.MIN_WIDTH and height<cls.MIN_HEIGHT:
      if width/cls.MIN_WIDTH < height/cls.MIN_HEIGHT:
        new_width = cls.MIN_WIDTH
        new_height = int(new_width*height/width) 
      else:
        new_height = cls.MIN_HEIGHT
        new_width = int(width*new_height/height) 

    size =  (new_width,new_height)
    return size

  @classmethod
  def resize(cls,image_path,size):
    '''
    Resize the image
    Parameter:
      image_path {str} : the local image path
      size {tuple,list} : (width,height)
    '''
    try:
      image = Image.open(image_path)
      image.resize(size).save(image_path)
      image.close()
      return True
    except Exception as e:
      return False



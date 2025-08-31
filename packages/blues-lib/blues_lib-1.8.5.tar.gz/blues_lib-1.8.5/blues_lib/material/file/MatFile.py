import sys,os,re,datetime
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.output.STDOut import STDOut
from type.file.File import File
from util.BluesDateTime import BluesDateTime    
from util.BluesImage import BluesImage    
from util.BluesFiler import BluesFiler    

class MatFile(File):
  
  # the material stack's root dir
  MATERIAL_DIR = 'material'
  MATERIAL_LOG_DIR = 'log'

  # the material statck's file
  STACK_FILE_NAME = 'stack.json'

  @classmethod
  def get_download_dir(cls,dirs=[]):
    today = BluesDateTime.get_today()
    subdirs = [cls.MATERIAL_DIR,today,*dirs]
    return cls.get_dir_path(subdirs)

  @classmethod
  def get_download_image(cls,site,id,url)->STDOut:
    '''
    Download the image in the body
    Parameter:
      site {str} : the site's name
      id {str} : the material's id
      url {str} : the image's online url
    '''
    if not site or not id or not url:
      return STDOut(500,'Failed to download - The parameters site,id,url are required',None)

    image_dir = cls.get_download_dir([site,id])
    result = BluesFiler.download_one(url,image_dir)
    if result[0]==200:
      # convert type and size
      download_path = result[1]
      # the filename may be changed
      converted_path = BluesImage.convert_type(download_path)
      BluesImage.convert_size(converted_path)
      return STDOut(200,'Managed to download',converted_path)
    else:
      return STDOut(500,f'Failed to download - {result[1]}',url)

  @classmethod
  def get_stack_file(cls):
    return cls.get_file_path(cls.MATERIAL_DIR,cls.STACK_FILE_NAME)
  
  @classmethod
  def get_stack_root(cls):
    return cls.get_dir_path(cls.MATERIAL_DIR)

  @classmethod
  def get_material_root(cls):
    return cls.get_dir_path(cls.MATERIAL_DIR)

  @classmethod
  def get_log_root(cls):
    return cls.get_dir_path(cls.MATERIAL_LOG_DIR)

  @classmethod
  def get_today_log_root(cls):
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    root = cls.get_log_root()
    return os.path.join(root,today)

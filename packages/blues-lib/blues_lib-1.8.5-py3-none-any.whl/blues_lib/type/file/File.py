import sys,os,re,time

sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from config.ConfigManager import config
from util.BluesURL import BluesURL   
from util.BluesFiler import BluesFiler    

class File():

  ROOT_DIR = config.get("app.rootdir")

  @classmethod
  def get_dir_path(cls,subdir=None):
    '''
    Get the blues lib's standard dir path
    Parameter:
      subdir {None|str|list} : the sub dirs
        None: return the root dir
        str: return the subdir
        list: return the multi subdir
    '''
    if not subdir:
      dir_path = cls.ROOT_DIR 
    else:
      dirs = subdir if type(subdir)==list else [subdir]
      # support multi level dirs
      dir_path = os.path.join(cls.ROOT_DIR,*dirs)

    # create dir
    BluesFiler.makedirs(dir_path)
    return dir_path 

  @classmethod
  def get_file_path(cls,subdir,filename):
    '''
    Get the file absolute path base the blues lib root dir
    Support add subdirs
    Parameter:
      subdir {str,list} : one or multi level dirs
      filename {str} : the filename
    '''
    dir_path = cls.get_dir_path(subdir)
    return os.path.join(dir_path,filename)

  @classmethod
  def get_domain_file_path(cls,url,subdir,extension='txt'):
    domain = BluesURL.get_main_domain(url)
    filename = '%s.%s' % (domain,extension)
    return cls.get_file_path(subdir,filename)

  @classmethod
  def get_file_name(cls,prefix='',name='',suffix='',extension=''):
    file_name = name if name else int(time.time()*1000)
    if prefix:
      file_name='%s-%s' % (prefix,file_name)
    if suffix:
      file_name='%s-%s' % (file_name,suffix)
    if extension:
      file_name='%s.%s' % (file_name,extension)
    return file_name 


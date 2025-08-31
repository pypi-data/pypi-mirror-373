import re
from os import path
from urllib.parse import urlparse
from tld import get_fld
from .BluesAlgorithm import BluesAlgorithm

class BluesURL():

  @classmethod
  def get_domain(cls,url):
    parsed_url = urlparse(url)
    return parsed_url.netloc

  @classmethod
  def get_main_domain(cls,url):
    return get_fld(url)
  
  @classmethod
  def get_abs_path(cls,abs_file,child_dir='',file_name=''):
    '''
    获取当前文件所在目录（或子目录下）的文件或目录的绝对路径
    @param {str} abs_file 当前文件绝对路径
    @param {str]} suffix 基于当前目录向后拼接的目录
    '''
    cur_path = path.dirname(abs_file)
    return path.join(cur_path,child_dir,file_name)
  
  @classmethod
  def get_file_name(cls,url,with_extension=True):
    parsed_url = urlparse(url)
    file_path = path.basename(parsed_url.path)
    file_name = path.splitext(file_path)[0]
    extend_name = path.splitext(file_path)[1]
    if len(file_name)>32:
      file_name = BluesAlgorithm.md5(file_name)
    if with_extension:
      return file_name+extend_name
    else:
      return file_name

  @classmethod
  def get_extend_name(cls,file_name):
    '''
    Return the file's textend name, contains the .
    '''
    return path.splitext(file_name)[1]

  @classmethod
  def get_file_path(cls,dir_path,file_name):
    return path.join(dir_path,file_name)

  @classmethod
  def get_file_dir(cls,file_path):
    '''
    Get the file path witout file name
    '''
    return path.dirname(file_path)

  @classmethod
  def rename_extend_name(cls,file_path,extend_name):
    if not extend_name:
      return file_path

    file_dir = cls.get_file_dir(file_path)
    pure_file_name = cls.get_file_name(file_path,False)
    new_file_name = '%s.%s' % (pure_file_name,extend_name)
    return path.join(file_dir,new_file_name)
    

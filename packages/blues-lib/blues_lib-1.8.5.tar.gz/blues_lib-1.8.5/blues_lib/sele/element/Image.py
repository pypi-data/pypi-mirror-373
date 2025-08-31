import sys,os,re,time
from .deco.InfoKeyDeco import InfoKeyDeco
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from sele.waiter.Querier import Querier  
from sele.element.Info import Info  
from type.file.File import File
from util.BluesFiler import BluesFiler

class Image():

  def __init__(self,driver):
    self.__driver = driver
    self.__querier = Querier(driver,5) 
    self.__info = Info(driver) 

  def download_image(self,image_CS_WE,image_dir=None,parent_CS_WE=None,timeout=5):
    '''
    Returns:
      {dict} : format download output, like:
        {'code':200,files:[],'message':''}
    '''
    image_CS_WEs = image_CS_WE if type(image_CS_WE)==list else [image_CS_WE]
    urls = self.get_img_urls(image_CS_WEs,parent_CS_WE,timeout)
    if urls:
      default_dir = File.get_dir_path(['download','img']) 
      file_dir = image_dir if image_dir else default_dir
      return BluesFiler.download(urls,file_dir)
    else:
      return None

  def get_img_urls(self,image_CS_WE,parent_CS_WE=None,timeout=5):
    '''
    Get all img urls from multiple selectors
    '''
    if not image_CS_WE:
      return None
    
    image_CS_WEs = image_CS_WE if type(image_CS_WE)==list else [image_CS_WE]

    urls = []
    for image_CS_WE in image_CS_WEs:
      if not image_CS_WE:
        continue
      current_urls = self.__get_img_urls(image_CS_WE,parent_CS_WE,timeout)
      if current_urls:
        urls.extend(current_urls)
    return urls

  def __get_img_urls(self,target_CS_WE,parent_CS_WE=None,timeout=5):
    '''
    Support img or other elements
    Returns:
      {list<str>} : the url list
    '''
    web_element = self.__querier.query(target_CS_WE,parent_CS_WE,timeout)
    if not web_element:
      return None
    urls = []
    if web_element.tag_name == 'img':
      url = self.__info.get_attr(web_element,'src')
      if url:
        urls.append(url)
    else:
      img_elements = self.__querier.query_all('img',web_element,timeout)
      if img_elements:
        for img_element in img_elements:
          url = self.__info.get_attr(img_element,'src')
          if url:
            urls.append(url)
    return urls



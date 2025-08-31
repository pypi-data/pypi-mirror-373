import sys,os,re,random,time
from selenium.webdriver.common.keys import Keys
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from sele.waiter.Querier import Querier  

class Input():

  def __init__(self,driver):
    self.__driver = driver
    self.__querier = Querier(driver,5)

  def write(self,target_CS_WE,value,parent_CS_WE=None,timeout=5):
    '''
    Clear and write text into the text controller
    Parameter:
      target_CS_WE {str | WebElement} : the input element's css selecotr or web element
      texts {list<str>} : one or more text string
    '''
    web_element = self.__querier.query(target_CS_WE,parent_CS_WE,timeout)
    if not web_element:
      return None

    self.clear(web_element,None)

    self.append(web_element,value,None)

  def append(self,target_CS_WE,value,parent_CS_WE=None,timeout=5):
    '''
    Append text into the text controller
    Parameter:
      target_CS_WE {str | WebElement} : the input element's css selecotr or web element
      texts {list<str>} : one or more text string
    '''
    texts = value if type(value)==list else [value]

    web_element = self.__querier.query(target_CS_WE,parent_CS_WE,timeout)
    if not web_element:
      return None

    web_element.send_keys(*texts)

  def write_para(self,target_CS_WE,value,LF_count=1,parent_CS_WE=None,timeout=5,input_by_para=True):
    '''
    Write lines with line break
    Parameter:
      target_CS_WE {str | WebElement} : the input element's css selecotr or web element
      parent_CS_WE {str | WebElement} : the input element parent's css selecotr or web element
      texts {list<str>} : texts
      LF_count {int} : line break count in every para
      input_by_para {bool} : input txt para by para
    '''
    texts = value if type(value)==list else [value]
    paras = self.__get_paras(texts,LF_count)

    if input_by_para:
      for para in paras:
        self.append(target_CS_WE,para,parent_CS_WE,timeout)
    else:
      self.write(target_CS_WE,paras,parent_CS_WE,timeout)

  def append_para(self,target_CS_WE,value,LF_count=1,parent_CS_WE=None,timeout=5):
    texts = value if type(value)==list else [value]
    paras = self.__get_paras(texts,LF_count)
    self.append(target_CS_WE,paras,parent_CS_WE,timeout)

  def __get_paras(self,texts,LF_count):
    break_texts = []
    idx = 0
    max_idx = len(texts)-1
    for text in texts:
      break_texts.append(text)
      if idx<=max_idx:
        for i in range(LF_count):
          break_texts.append(Keys.ENTER)
      idx+=1
    return break_texts

  def write_discontinuous(self,target_CS_WE,text,parent_CS_WE=None,timeout=5):
    web_element = self.__querier.query(target_CS_WE,parent_CS_WE,timeout)
    if not web_element:
      return None

    self.clear(web_element,None)
    self.append_discontinuous(web_element,text,None)
  
  def append_discontinuous(self,target_CS_WE,text,parent_CS_WE=None,timeout=5):
    '''
    Input chars non-uniform speed
    '''
    texts = text if type(text)==list else [text]
    web_element = self.__querier.query(target_CS_WE,parent_CS_WE,timeout)

    for text in texts:
      # input char by char
      for char in text:
        self.__input_discontinuous(web_element,char)

  def __input_discontinuous(self,web_element,char,min=0.2,max=1.5):
    '''
    input the text one char by one char intermittently
    using a random interval
    '''
    interval = round(random.uniform(min,max),1)
    time.sleep(interval)
    web_element.send_keys(char)

  def clear(self,target_CS_WE,parent_CS_WE=None,timeout=5):
    web_element = self.__querier.query(target_CS_WE,parent_CS_WE,timeout)
    web_element.clear()

import smtplib
from typing import List
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.header import Header
import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from util.BluesDateTime import BluesDateTime
from type.output.STDOut import STDOut

class BluesMailer():

  config = {
    # pick a smtp server
    'server' : 'smtp.qq.com',
    'port' : 465,
    # debug level: 0 - no message; 1 - many messages
    'debug_level' : 0, 
    # the sender's address
    'addresser' : '1121557826@qq.com',
    'addresser_name' : 'BluesLiu QQ',
    # the qq's auth code (not the account's login password)
    'addresser_pwd' : 'ryqokljshrrlifae',
  }

  __instance = None

  @classmethod
  def get_instance(cls):
    if not cls.__instance:
      cls.__instance = BluesMailer()
    return cls.__instance

  def __init__(self):
    self.connection = self.__get_connection()

  def __get_connection(self):
    connection = smtplib.SMTP_SSL(self.config['server'],self.config['port'])
    connection.set_debuglevel(self.config['debug_level'])
    connection.login(self.config['addresser'],self.config['addresser_pwd'])
    return connection

  def send(self,payload)->STDOut:
    '''
    @description : send the mail
    @param {MailPayload} payload : mail's required info
     - addressee ：list | str  ; required
     - addressee_name ：str , can't contains space
     - subject : str ; required
     - content : str 
    @returns {STDOut} : send result

    '''
    # the receiver's address
    if not payload.get('addressee'):
      return STDOut(501,'The addressee address is empty!')
    
    if not payload.get('subject'):
      return STDOut(502,'The mail subject is empty!')

    if not payload.get('content'):
      return STDOut(503,'The mail content is empty!')
    
    try:
      message = self.__get_message(payload)
      self.connection.sendmail(self.config['addresser'],payload['addressee'],message)
      self.connection.quit()
    except Exception as e:
      return STDOut(504,f'Failed to send - {e}')

    return STDOut(200,'Managed to send')

  @classmethod
  def get_title_with_time(self,title):
    return '%s - %s' % (title,BluesDateTime.get_now())

  @classmethod
  def get_html_body(cls,title:str,para:str,urls:List[dict]=None,detail:str=''):
    now = BluesDateTime.get_now()
    link = ''
    if urls:
      for url in urls:
        link += '''
          <p><a href="{}" style="font-size:16px;color:#07c;margin-top:1rem;">{}</a></p>
        '''.format(url['href'],url['text'])

    body = '''
    <div style="padding:0 5%;">
      <h1 style="margin:5rem 0 2rem 0;">{}</h1>
      <p style="color:gray;font-size:14px;">DateTime: {}</p>
      <p style="line-height:26px;font-size:16px;">{}</p>
      {}
      <p style="line-height:26px;font-size:16px;">{}</p>
    </div>
    '''.format(title,now,para,link,detail)

    return body

  def __get_message(self,payload):
    message = MIMEMultipart()
    
    message['subject'] = payload['subject']
    # the last string must be from mail address
    from_with_nickname = '%s <%s>' % (self.config['addresser_name'],self.config['addresser']) 
    message['from'] = Header(from_with_nickname)

    if type(payload['addressee'])==str:
      message['to'] = Header(payload.get('addressee_name',payload['addressee']))
    else:
      message['to'] = Header(','.join(payload['addressee']))

    # support html document
    img_html = self.__get_img_html(message,payload.get('images'))
    message.attach(MIMEText(payload['content'] + img_html, 'html'))
    return message.as_string()

  def __get_img_html(self,message,images):
    if not images:
      return ''
    
    html = ''
    i=0
    for image in images:
      with open(image, 'rb') as file:
        img = MIMEImage(file.read())
      i+=1
      cid = 'image%s' % i
      img.add_header('Content-ID', '<%s>' % cid)
      message.attach(img)
      html += '<p><img style="width:100%;" src="cid:{}"/></p>'.format(cid)
    return '<div style="padding:10px 10%;">{}</div>'.format(html)

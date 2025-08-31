import sys,os,re

sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.output.STDOut import STDOut
from util.BluesMailer import BluesMailer  
from command.NodeCommand import NodeCommand
from util.BluesFiler import BluesFiler
from namespace.CommandName import CommandName

class Email(NodeCommand):

  NAME = CommandName.Notifier.EMAIL

  def _invoke(self)->STDOut:
    payload = self.get_payload()
    mailer = BluesMailer.get_instance()
    return mailer.send(payload)
      
  def get_payload(self)->dict:

    title = f'{self._output.code} - {self._output.message}'
    content = self._get_content(title)
    subject = BluesMailer.get_title_with_time(title)
    return {
      'subject':subject,
      'content':content,
      'images':None,
      'addressee':['langcai10@dingtalk.com'], # send to multi addressee
      'addressee_name':'BluesLiu',
    }

  def _get_content(self,title:str)->str:
    detail = self._get_log()
    para = f'{self._output.data}'
    return BluesMailer.get_html_body(title,para,None,detail)
    
  def _get_log(self):
    file = self._logger.file
    separator = self._logger.separator
    content = BluesFiler.read(file)
    if content:
      # retain the latest one
      items = content.split(separator)
      non_empty_items = [item.strip() for item in items if item.strip()]
      content = non_empty_items[-1] if non_empty_items else content
      
      # break line
      content = content.replace('\n','<br/>')
      # dash line
      pattern = r'[-=]{10,}'
      content = re.sub(pattern, '----------', content)
    return content
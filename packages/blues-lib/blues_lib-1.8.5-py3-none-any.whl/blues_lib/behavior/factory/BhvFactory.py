import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.factory.Factory import Factory
from type.model.Model import Model

from behavior.bean.Attr import Attr
from behavior.bean.CSS import CSS
from behavior.bean.Choice import Choice
from behavior.bean.File import File
from behavior.bean.Input import Input
from behavior.bean.AuthCodeInput import AuthCodeInput
from behavior.bean.Select import Select
from behavior.bean.Screenshot import Screenshot
from behavior.bean.Text import Text
from behavior.bean.Textarea import Textarea
from behavior.bean.Value import Value
from behavior.bean.FileCookie import FileCookie
from behavior.bean.BrCookie import BrCookie
from behavior.bean.Url import Url
from behavior.bean.Copy import Copy
from behavior.bean.Paste import Paste

from behavior.event.Click import Click
from behavior.event.Keyboard import Keyboard
from behavior.event.Framein import Framein
from behavior.event.Frameout import Frameout
from behavior.event.Hover import Hover
from behavior.event.Remove import Remove
from behavior.event.Rollin import Rollin
from behavior.event.Open import Open
from behavior.event.Quit import Quit

from behavior.checker.ElePresents import ElePresents
from behavior.checker.EleAbsents import EleAbsents
from behavior.checker.EleInvisible import EleInvisible
from behavior.checker.UrlChanges import UrlChanges
from behavior.checker.UrlContains import UrlContains
from behavior.checker.UrlToBe import UrlToBe
from behavior.checker.UrlMatches import UrlMatches
from behavior.checker.ToBeClickable import ToBeClickable
from behavior.checker.ToBeSelected import ToBeSelected
from behavior.checker.ToBePresence import ToBePresence
from behavior.checker.ToBeVisible import ToBeVisible

from behavior.general.Wait import Wait
from behavior.general.Email import Email

class BhvFactory(Factory):
  def __init__(self,model:Model,browser=None):
    self._model = model
    self._browser = browser

  def create_attr(self):
    return Attr(self._model,self._browser)
  
  def create_css(self):
    return CSS(self._model,self._browser)
  
  def create_choice(self):
    return Choice(self._model,self._browser)
  
  def create_file(self):
    return File(self._model,self._browser)
  
  def create_input(self):
    return Input(self._model,self._browser)
  
  def create_auth_code_input(self):
    return AuthCodeInput(self._model,self._browser)
  
  def create_select(self):
    return Select(self._model,self._browser)
  
  def create_screenshot(self):
    return Screenshot(self._model,self._browser)
  
  def create_text(self):
    return Text(self._model,self._browser)
  
  def create_textarea(self):
    return Textarea(self._model,self._browser)
  
  def create_value(self):
    return Value(self._model,self._browser)
  
  def create_file_cookie(self):
    return FileCookie(self._model,self._browser)
  
  def create_br_cookie(self):
    return BrCookie(self._model,self._browser)
  
  def create_url(self):
    return Url(self._model,self._browser)
  
  def create_copy(self):
    return Copy(self._model,self._browser)
  
  def create_paste(self):
    return Paste(self._model,self._browser)
  
  def create_click(self):
    return Click(self._model,self._browser)
  
  def create_keyboard(self):
    return Keyboard(self._model,self._browser)
  
  def create_framein(self):
    return Framein(self._model,self._browser)
  
  def create_frameout(self):
    return Frameout(self._model,self._browser)
  
  def create_hover(self):
    return Hover(self._model,self._browser)
  
  def create_remove(self):
    return Remove(self._model,self._browser)
  
  def create_rollin(self):
    return Rollin(self._model,self._browser)
  
  def create_open(self):
    return Open(self._model,self._browser)
  
  def create_quit(self):
    return Quit(self._model,self._browser)
  
  def create_ele_presents(self):
    return ElePresents(self._model,self._browser)
  
  def create_ele_absents(self):
    return EleAbsents(self._model,self._browser)
  
  def create_ele_invisible(self):
    return EleInvisible(self._model,self._browser)

  def create_url_changes(self):
    return UrlChanges(self._model,self._browser)
    
  def create_url_contains(self):
    return UrlContains(self._model,self._browser)
  
  def create_url_to_be(self):
    return UrlToBe(self._model,self._browser)
  
  def create_url_matches(self):
    return UrlMatches(self._model,self._browser)
  
  def create_to_be_clickable(self):
    return ToBeClickable(self._model,self._browser)

  def create_to_be_selected(self):
    return ToBeSelected(self._model,self._browser)
  
  def create_to_be_presence(self):
    return ToBePresence(self._model,self._browser)
  
  def create_to_be_visible(self):
    return ToBeVisible(self._model,self._browser)
  
  def create_wait(self):
    return Wait(self._model)
  
  def create_email(self):
    return Email(self._model)
  
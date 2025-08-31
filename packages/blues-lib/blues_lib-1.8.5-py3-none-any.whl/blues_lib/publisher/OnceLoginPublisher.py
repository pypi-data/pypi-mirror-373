import sys,os,re
from .Publisher import Publisher

class OnceLoginPublisher(Publisher):

  def login(self):
    self.browser = self.loginer.login()
    if not self.browser:
      raise Exception('Login failure')
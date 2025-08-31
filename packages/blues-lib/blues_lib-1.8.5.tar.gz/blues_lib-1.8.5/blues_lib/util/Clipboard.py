import pyperclip

class Clipboard():
  
  @classmethod
  def paste(cls)->str:
    '''
    Get the text from the os's clipboard
    '''
    return pyperclip.paste()
  
  @classmethod
  def copy(cls,text)->None:
    '''
    Set text to the os's clipboard
    '''
    return pyperclip.copy(text)

  @classmethod
  def clear(cls):
    '''
    Clear the os's clipboard
    '''
    pyperclip.copy('')

import sys,pyautogui,time

class AutoGUI():
  
  @classmethod
  def paste(cls)->str:
    '''
    execute the ctrl/command+v
    '''
    if sys.platform == "darwin":  
      # macOS
      pyautogui.hotkey('command', 'v')
    else:  
      # Windows and Linux
      pyautogui.hotkey('ctrl', 'v')
      
  @classmethod
  def copy(cls)->bool:
    '''
    Must focus the target first
    Execute the ctrl/command+c
    '''
    if sys.platform == "darwin":  
      # macOS
      pyautogui.hotkey('command', 'a')
      pyautogui.hotkey('command', 'c')
    else:  
      # Windows and Linux
      pyautogui.hotkey('ctrl', 'a')
      pyautogui.hotkey('ctrl', 'c')

  
  @classmethod
  def press(cls,key:str)->bool:
    if key == 'esc' and sys.platform == "darwin":
      pyautogui.press('enter')

    time.sleep(0.1)
    pyautogui.press(key)
    return True
  


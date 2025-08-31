import os,re,sys
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from util.BluesResource import BluesResource

class ResReader:
  
  @classmethod
  def read(cls,addr:str,root:str='',ext:str='conf'):
    """
    Read metadata from a specified address.
    Args:
      addr (str): The address specifying the package and file to read metadata from.
      root (str): The root path of the resource.
      ext (str): The file extension.
    Returns:
      The loaded metadata.
    """
    package, file = addr.rsplit('.', 1) 
    package = f'{root}.{package}' if root else package
    file = f'{file}.{ext}'
    return cls.load(package,file)
  
  @classmethod
  def load(cls,package:str, file: str):
    try: 
      config = BluesResource.read_hocon(package, file)
      return config
    except Exception as e:
      print(f"hocon error: {e}")
      return None
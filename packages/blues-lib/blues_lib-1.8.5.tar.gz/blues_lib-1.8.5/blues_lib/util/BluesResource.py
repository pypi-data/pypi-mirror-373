import yaml,json5,json
from importlib import resources
import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from util.BluesFiler import BluesFiler
from util.BluesHocon import BluesHocon

class BluesResource:
  '''
  @description : support json json5 yaml hocon files read from package resources
  '''

  @classmethod
  def read(cls,package: str,file: str):
    with resources.open_text(package, file, encoding='utf-8') as f:
      return f.read()

  @classmethod
  def read_yaml(cls,package: str,file: str):
    try:
      return yaml.safe_load(cls.read(package, file))
    except Exception as e:
      print(f"yaml error: {e}")
      return None

  @classmethod
  def read_json5(cls,package: str,file: str):
    try:
      return json5.loads(cls.read(package, file))
    except Exception as e:
      print(f"json5 error: {e}")
      return None

  @classmethod
  def read_hocon(cls,package: str,file: str,as_dict=True):
    try:
      json_config = BluesHocon.parse_file(package, file)
      return BluesFiler.config_to_dict(json_config) if as_dict else json_config
    except Exception as e:
      print(f"hocon error: {e}")
      return None

  @classmethod
  def read_json(cls,package: str,file: str):
    try: 
      return json.loads(cls.read(package, file))
    except Exception as e:
      print(f"json error: {e}")
      return None
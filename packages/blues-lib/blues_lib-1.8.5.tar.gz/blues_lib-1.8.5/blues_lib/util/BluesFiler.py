import os,re,sys,requests,json,csv,base64,yaml,json5
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from pyhocon import ConfigFactory
from datetime import datetime,timedelta
from util.BluesURL import BluesURL
from util.BluesConsole import BluesConsole

class BluesFiler:
  
  @classmethod
  def get_app_path(cls)->str:
    from config.ConfigManager import config
    cur_path = os.path.realpath(__file__)
    root_dir = config.get('app.root')
    return os.path.join(cur_path.split(root_dir)[0],root_dir)
  
  @classmethod
  def get_abs_path(cls,path:str)->str:
    root_path = cls.get_app_path()
    return os.path.join(root_path,path)
  
  @classmethod 
  def get_abs_path_from_mod_path(cls,mod_path:str,ext:str='')->str:
    file_path = cls.to_file_path(mod_path,ext)
    return cls.get_abs_path(file_path)

  @classmethod
  def to_file_path(cls,mod_path:str,ext:str='')->str:
    '''
    convert the module path to file path
    '''
    file_path = os.path.join(*mod_path.split("."))
    if ext:
      file_path += f'.{ext}'
    return file_path

  @classmethod
  def readfiles(cls,directory):
    '''
    Read the file list in a dir, don't support the next dirs
    @param {string} directory 
    '''
    file_list = []
    for root, dirs, files in os.walk(directory):
      for file in files:
        file_list.append(os.path.join(root, file))
    return file_list

  @classmethod
  def removedirs(cls,directory,retention_days=0):
    '''
    @description Remove all child dir and files
    @param {string} directory 
    '''
    threshold = datetime.now() - timedelta(days=retention_days)
    removed_count = 0
    if not cls.exists(directory):
      return removed_count

    for root, dirs, files in os.walk(directory):
      for file in files:
        file_path = os.path.join(root, file)
        file_modified_time = datetime.fromtimestamp(os.path.getmtime(file_path))
        if file_modified_time < threshold:
          os.remove(file_path)
          removed_count +=1
      for dire in dirs:
        dir_path = os.path.join(root, dire)
        file_modified_time = datetime.fromtimestamp(os.path.getmtime(dir_path))
        if file_modified_time < threshold:
          # recursion to remove the dir
          removed_count += cls.removedirs(dir_path,retention_days)
    # remove the base dir
    if cls.is_dir_empty(directory):
      os.rmdir(directory)
      removed_count +=1
    return removed_count

  @classmethod
  def is_dir_empty(cls,dir_path):
    return not bool(os.listdir(dir_path))

  @classmethod
  def download(cls,urls,directory,success=None,error=None):
    '''
    @description Download multi files
    @param {list|str} urls files' remote url
    @param {string} directory : Local directory to save the downloaded files
    @param {function} success : Callback function called on success
    @param {function} error : Callback function called on failure
    @returns {dict} complex result
    '''
    result = cls.__get_result()
    if not urls:
      return result 
    
    url_list = urls if type(urls)==list else [urls]
    for url in url_list:
      # download the image
      (code,file_or_msg) = cls.download_one(url,directory)
      if code == 200:
        item = {
          'url':url,
          'file':file_or_msg,
          'callback_value':None
        }
        if success:
          item['callback_value'] = success(file_or_msg)
        result['success']['count']+=1
        result['success']['files'].append(item)
        result['files'].append(file_or_msg)
        result['code'] = 200
      else:
        item = {
          'url':url,
          'message':file_or_msg,
          'callback_value':None
        }
        if error:
          item['callback_value'] = error(str(e))
        result['error']['count']+=1
        result['error']['files'].append(item)
    
    return result 

  @classmethod
  def download_one(cls,url,directory):
    '''
    @description : download one file
    @param {str} url : file's remote url
    @param {str} directory : The dir to save the download file
    '''
    try:
      # Ensure directory existence
      cls.makedirs(directory)
      # Keep the file name unchanged
      #file_name = url.split('/')[-1]
      file_name = BluesURL.get_file_name(url)
      local_file = os.path.join(directory,file_name)

      # The timeout period must be set, otherwise the request will not stop automatically
      BluesConsole.info('Downloading the file: %s' % url)
      res=requests.get(url,timeout=1)
      res.raise_for_status()
      with open(local_file,'wb') as f:
        f.write(res.content)
        f.close()
        BluesConsole.success('Downloaded the file: %s' % url)
        return (200,local_file) 
    except Exception as e:
      BluesConsole.error('Downloaded the image failure: %s' % e)
      return (500,str(e))

  @classmethod
  def read(cls,file_path)->str:
    try:
      with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()
    except Exception as e:
      return ''

  @classmethod
  def read_yaml(cls,file_path):
    try:
      with open(file_path, 'r', encoding='utf-8') as file:
        return yaml.safe_load(file)
    except Exception as e:
      print(f"yaml error: {e}")
      return None

  @classmethod
  def read_json5(cls,file_path):
    try:
      with open(file_path, 'r', encoding='utf-8') as file:
        data = json5.load(file)
        return data
    except Exception as e:
      print(f"json5 error: {e}")
      return None

  @classmethod
  def read_hocon(cls,path:str,as_dict=True,dash_to_dot=True):
    '''
    @description: read conf file 
    @param {str} path: file path or mod path
    @param {bool} as_dict: return dict or ConfigTree
    @param {bool} dash_to_dot: convert dash to dot in all dict's keys
    @returns {dict|ConfigTree}
    '''
    try:
      file_path = ''
      if os.path.isabs(path):
        file_path = path
      else:
        if path.find('.conf')==-1:
          file_path = cls.get_abs_path_from_mod_path(path,'conf')
        else:
          file_path = cls.get_abs_path(path)

      config = ConfigFactory.parse_file(file_path)
      if not as_dict:
        return config

      conf = cls.config_to_dict(config)
      return cls.replace_dashes_with_dots(conf) if dash_to_dot else conf
    except Exception as e:
      print(f"hocon error: {e}")
      return None

  @classmethod
  def replace_dashes_with_dots(cls,data):
    """
    递归处理字典或列表，将所有键名中的 `-` 替换为 `.`
    
    参数:
        data: 可能包含字典、列表的任意对象
        
    返回:
        处理后的新对象（原对象不会被修改）
    """
    # 处理字典类型
    if isinstance(data, dict):
      new_dict = {}
      for key, value in data.items():
        # 替换键名中的 `-` 为 `.`
        new_key = key.replace('-', '.')
        # 递归处理值
        new_value = cls.replace_dashes_with_dots(value)
        new_dict[new_key] = new_value
      return new_dict
    
    # 处理列表类型
    elif isinstance(data, list):
      new_list = []
      for item in data:
        # 递归处理每个元素
        new_item = cls.replace_dashes_with_dots(item)
        new_list.append(new_item)
      return new_list
    
    # 其他类型（如字符串、数字等）直接返回
    else:
      return data

  @classmethod
  def config_to_dict(cls,config):
    if isinstance(config, dict):
      return {k: cls.config_to_dict(v) for k, v in config.items()}
    elif isinstance(config, list):
      return [cls.config_to_dict(v) for v in config]
    elif hasattr(config, 'to_dict'):  # 处理 pyhocon 的 ConfigTree
      return cls.config_to_dict(config.to_dict())
    else:
      return config

  @classmethod
  def read_json(cls,file_path):
    try:
      with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        return data
    except Exception as e:
      print(f"json error: {e}")
      return None

  @classmethod
  def write_json(cls,file_path,data,indent=2):
    dir_path = os.path.dirname(file_path)
    if dir_path!='.':
      cls.makedirs(dir_path)

    try:
      with open(file_path, 'w', encoding='utf-8') as file:
        # must set ensure_ascii as False for Chinese character
        json.dump(data,file,indent=indent,ensure_ascii=False)
        return file_path
    except Exception as e:
      print('==>e',e)
      return None

  @classmethod
  def read_csv(cls,file_path,headless=False):
    '''
    @description : read csv file
    @param {str} file_path
    @returns {list<list>}
    '''
    try:
      with open(file_path, 'r', encoding='utf-8',errors='ignore') as file:
        lines = csv.reader(file) 
        rows = []
        i=0
        for line in lines:
          i+=1
          if i==1 and headless:
            continue
          if not line:
            continue
          rows.append(line)
        return rows
    except Exception as e:
      return None


  @classmethod
  def write_csv(cls,file_path,rows,header=None,mode='w'):
    '''
    @description : write to csv file
    @param {str} file_path : the csv file's path
    @param {list<list>|tuple<tuple>} rows : the data rows
    @param {list|tuple} header
    @param {str} mode : 'a' - append ; 'w' - cover
    '''
    dir_path = os.path.dirname(file_path)
    if dir_path!='.':
      cls.makedirs(dir_path)

    try:
      with open(file_path, mode, encoding='utf-8',newline="") as file:
        writer = csv.writer(file) 
        if mode=='w' and header:
          writer.writerow(header)
        if rows:
          for row in rows:
            writer.writerow(row)
        return True
    except Exception as e:
      return None

  @classmethod
  def __get_result(cls):
    return {
      'code':500,
      'files':[],
      'success':{
        'count':0,
        'files':[],
      },
      'error':{
        'count':0,
        'files':[],
      },
    }

  @classmethod
  def write(cls,file_path,text,mode='w')->bool:
    '''
    @description : write text to file
    @param {str} file_path : file's path
    @param {str} text : content
    @param {str} mode : write mode
      - 'w' : clear the history content
      - 'a' : append text
    @returns {str} : the writed file path
    '''
    dir_path = os.path.dirname(file_path)
    if dir_path!='.':
      cls.makedirs(dir_path)

    try:
      with open(file_path,mode,encoding='utf-8') as file:
        file.write(text)
      return True
    except Exception as e:
      return False

  @classmethod
  def write_after(cls,file_path,text):
    cls.write(file_path,text,'a')

  @classmethod
  def exists(cls,path):
    '''
    @description : Does a dir or file exist
    @param {str} path
    @returns {bool} 
    '''
    return os.path.exists(path)

  @classmethod
  def filter_exists(cls,files):
    exists_files = []
    for file in files:
      if not cls.exists(file):
        continue
      exists_files.append(file)
    return exists_files

  @classmethod
  def makedirs(cls,path):
    '''
    @description : Create dirs (support multilevel directory) if they don't exist
    @param {str} path : multilevel dir
    @returns {None}
    '''
    if not cls.exists(path):
      os.makedirs(path)

  @classmethod
  def get_rename_file(cls,file_path,new_name='',prefix='',suffix='',separator='-'):
    '''
    @description : get the new file name path
    '''
    path_slices = file_path.split('/')
    original_name = path_slices[-1]
    copy_name = new_name if new_name else original_name
    if prefix:
      copy_name = prefix+separator+copy_name
    if suffix:
      copy_name = copy_name+separator+suffix
    path_slices[-1]=copy_name
    copy_path='/'.join(path_slices)
    return copy_path

  @classmethod
  def removefiles(cls,directory,retention_days=0):
    '''
    @description : clear files before n days
    @param {str} directory
    @param {int} retention_days : default 7
    @returns {int} deleted files count
    '''
    # 转换天数到时间间隔
    threshold = datetime.now() - timedelta(days=retention_days)
    removed_count = 0
    # 遍历目录
    for item in os.scandir(directory):
      try:
        # 获取文件的最后修改时间
        file_modified_time = datetime.fromtimestamp(os.path.getmtime(item.path))
        # 如果文件的最后修改时间早于阈值，则删除文件
        if os.path.isfile(item.path) and file_modified_time < threshold:
          os.remove(item.path)
          removed_count +=1
      except OSError as e:
        pass

    return removed_count

  @classmethod
  def dump_base64(cls,text):
    # 只接受bytes类型 b'xx'，且返回bytes，将其转为字符串
    return base64.b64encode(text.encode()).decode()

  @classmethod
  def load_base64(cls,b64):
    # 只接受bytes类型 b'xx'，且返回bytes，将其转为字符串
    return base64.b64decode(b64.encode()).decode()

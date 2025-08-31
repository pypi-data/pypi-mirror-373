import pandas

class BluesCSV():
  
  @classmethod
  def read(cls,csv_file):
    df = pandas.read_csv(csv_file)
    return df

  @classmethod
  def read_head(cls,csv_file):
    '''
    Returns {str} : multi original lines at the beginning
    '''
    df = cls.read(csv_file)
    return df.head()

  @classmethod
  def read_rows(cls,csv_file):
    df = cls.read(csv_file)
    return df.to_dict(orient='records')
  
  @classmethod
  def write(cls,file_path,rows,columns=None,index=False):
    '''
    Create or cover a csv file
    @param {str} file_path : the csv file abs path
    @param {list<list> | list<dict>} rows 
    @param {list<str>} columns : the csv's header - first row
      - if the item is a dict, don't need 
    @param {bool} index : create a index column
    '''
    if isinstance(rows[0],dict):
      df = pd.DataFrame(rows)
    else:
      df = pd.DataFrame(rows, columns=columns)
    df.to_csv(file_path, index=index) 

  @classmethod
  def append(cls,file_path,rows,index=False):
    '''
    Append rows to a exists csv file
    @param {str} file_path : the csv file abs path
    @param {list<list> | list<dict>} rows 
    @param {list<str>} columns : the csv's header - first row
      - if the item is a dict, don't need 
    @param {bool} index : create a index column
    '''
    df = pd.DataFrame(rows)
    df.to_csv(file_path,mode='a',header=False,index=index) 

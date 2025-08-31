import sys,os,re
sys.path.append(re.sub('test.*','blues_lib',os.path.realpath(__file__)))
from typing import List
from type.output.SQLSTDOut import SQLSTDOut
from dao.sql.BluesMySQL import BluesMySQL
from dao.sql.BluesSQLConvertor import BluesSQLConvertor
from config.ConfigManager import config

class BluesSQLIO():

  def __init__(self,account:dict=None):
    '''
    @param {dict} account 
    {
      'host':'localhost',
      'user':'root',
      'password':'',
      'database':'infocollection',
    }
    '''
    account = account if account else config.get("database")
    self.sql_executor = BluesMySQL.get_instance(account)

  def get(self,table:str,fields="*",conditions=None,orders=None,pagination=None)->SQLSTDOut:
    '''
    @description 查询用户提交数据
    @param {dict[]} conditions : one or more conditions
      [
        {'operator':'and','field':'name','comparator':'=','value':'blues','value_type':'str'},
        {'operator':'and','field':'name','comparator':'=','value':'blues'}
      ] 
    @param {dict[]} : orders
      [{'field':'id','sort':'asc'},{'field':'name','sort':'desc'}] 
    @param {dict} pagination : page info
      {'no':1,'size':10}
    @returns {SQLSTDOut}
    '''
    condition_sql = BluesSQLConvertor.get_condition_sql(conditions)
    order_sql = BluesSQLConvertor.get_order_sql(orders)
    limit_sql = BluesSQLConvertor.get_limit_sql(pagination)
    if isinstance(fields,str):
      field_sql = fields 
    elif isinstance(fields,list) or isinstance(fields,tuple): 
      field_sql = ','.join(fields)
    else:
      field_sql = '*'

    sql = 'select %s from %s %s %s %s' % (field_sql,table,condition_sql,order_sql,limit_sql)  
    return self.sql_executor.get(sql) 

  def insert(self,table:str,entities:List[dict])->SQLSTDOut:
    '''
    @description : insert by sql
    @param {dict | dict[]} entities : the entity dict's key is the real table field
      [{'name':'blues','age':18}]
    @returns {SQLSTDOut} 
    '''
    insert_sql = BluesSQLConvertor.get_insert_sql(entities)
    sql = 'insert into %s %s' % (table,insert_sql)
    return self.sql_executor.post(sql) 
 
  def post(self,table:str,fields:list,values:List[list])->SQLSTDOut:
    '''
    @description : insert by template sql
    @param {list|tuple} fields : the fields will be updated
      ['name','age']
    @param {list | list[]} values : one or multi row data values
      [['post01',1],['post02',2]]
    @returns {SQLResult} 
    '''
    insert_sql = BluesSQLConvertor.get_insert_template_sql(fields)
    sql = 'insert into %s %s' % (table,insert_sql)
    return self.sql_executor.post(sql,values) 
  
  def put(self,table:str,fields:list,values:list,conditions:List[dict])->SQLSTDOut:
    '''
    @description : update row
    @param {list|tuple} fields : the fields will be updated
      ['name','age']
    @param {list|tuple} values : the values will be writed
      ['blues',18]
    @param {dict[]} conditions : one or more conditions
      [
        {'operator':'and','field':'name','comparator':'=','value':'blues'},
        {'operator':'and','field':'name','comparator':'=','value':'blues'}
      ] 
    @returns {SQLResult} 
    '''
    update_sql = BluesSQLConvertor.get_update_template_sql(fields,conditions)
    sql = 'update %s %s' % (table,update_sql)
    return self.sql_executor.put(sql,values) 

  def update(self,table:str,entity:dict,conditions:List[dict])->SQLSTDOut:
    '''
    @description : update row
    @param {dict} entity : the entity dict's key is the real table field
      {'name':'blues','age':18}
    @param {dict[]} conditions : one or more conditions
      [
        {'operator':'and','field':'name','comparator':'=','value':'blues'},
        {'operator':'and','field':'name','comparator':'=','value':'blues'}
      ] 
    @returns {SQLResult} 
    '''
    update_sql = BluesSQLConvertor.get_update_sql(entity,conditions)
    sql = 'update %s %s' % (table,update_sql)
    return self.sql_executor.put(sql) 
  
  def delete(self,table:str,conditions:List[dict])->SQLSTDOut:
    '''
    @description : delete rows by conditon 
    @param {str} table 
    @param {dict[]} conditions : one or more conditions
      [
        {'operator':'and','field':'name','comparator':'=','value':'blues'},
        {'operator':'and','field':'name','comparator':'=','value':'blues'}
      ] 
    @returns {SQLResult}
    '''
    condition_sql = BluesSQLConvertor.get_condition_sql(conditions)
    sql = 'delete from %s %s' % (table,condition_sql)
    return self.sql_executor.delete(sql)   

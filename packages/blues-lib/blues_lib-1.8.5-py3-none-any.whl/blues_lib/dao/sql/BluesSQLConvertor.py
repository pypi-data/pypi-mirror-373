from pymysql.converters import escape_string

class BluesSQLConvertor():

  @classmethod
  def get_in_sql(cls,condition):
    '''
    @description : convert list or tuple to in sql
    @param {dict} condition  
      {'field':'name','values':['a','b','c']}
    @returns {str} : in sql
    '''
    sql = ''
    field = condition.get('field','')
    values = condition.get('values')

    if not values:
      return ''

    for value in values:
      sql += '"%s",' % value 
    return ' %s in (%s) ' % (field,sql[:-1])

  @classmethod
  def get_order_sql(cls,orders):
    '''
    @description : return order by sql
    @param {dict[]} : orders
      [{'field':'id','sort':'asc'},{'field':'name','sort':'desc'}] 
    @returns {str} : order by sql
    '''
    sql = ''
    if not orders:
      return sql

    order_list = [orders] if isinstance(orders,dict) else orders 
    for order in order_list:
      field = order.get('field')
      sort = order.get('sort')

      if not field:
        continue

      sql += '%s %s,' % (field,sort)

    if not sql:
      return ''

    return ' order by %s ' % sql[:-1] 

  @classmethod
  def get_update_template_sql(cls,fields,conditions):
    '''
    @description : convert dict to update sql
    @param {list|tuple} fields : the fields will be udpated
      ['name','age']
    @param {dict[]} conditions : one or more conditions
      [
        {'operator':'and','field':'name','comparator':'=','value':'blues','value_type':'str'},
        {'operator':'and','field':'name','comparator':'=','value':'blues'}
      ] 
    @returns {str} : update sql
    '''
    sql = ''
    condition_sql = cls.get_condition_sql(conditions)
    for field in fields:
      sql += field+'=%s,' # don't wrapper by ""
    return ' set %s %s ' % (sql[:-1],condition_sql)

  @classmethod
  def get_update_sql(cls,entity,conditions):
    '''
    @description : convert dict to update sql
    @param {dict} entity : the entity dict's key is the real table field
      {'name':'blues','age':18}
    @param {dict[]} conditions : one or more conditions
      [
        {'operator':'and','field':'name','comparator':'=','value':'blues'},
        {'operator':'and','field':'name','comparator':'=','value':'blues'}
      ] 
    @returns {str} : update sql
    '''
    sql = ''
    condition_sql = cls.get_condition_sql(conditions)
    for field in entity:
      sql += '%s="%s",' % (field,escape_string(entity[field]))
    return ' set %s %s ' % (sql[:-1],condition_sql)

  @classmethod
  def get_insert_template_sql(cls,fields):
    '''
    @description : convert dict to insert sql
    @param {str[]} fields : the fields will be insert
      ['name','age']
    @returns {str} : insert template sql
    '''
    key_sql = ''
    value_sql = ''
    
    for field in fields:
      key_sql += '%s,' % field
      value_sql += '%s,'

    return ' (%s) values (%s) ' % (key_sql[:-1],value_sql[:-1])

  @classmethod
  def get_insert_sql(cls,entities):
    '''
    @description : convert dict to insert sql
    @param {dict|dict[]} entities : the entity dict's key is the real table field
      [{'name':'blues','age':18}]
    @returns {str} : insert sql
    '''
    entity_list = [entities] if isinstance(entities,dict) else entities
    key_sql = ''
    value_sql = ''
    
    first_entity = entity_list[0]
    for key in first_entity:
      key_sql += '%s,' % key

    for entity in entity_list:    
      unit_value_sql = ''
      for key in entity:
        # must use escape_string to deal Quote collision problem
        escape_value = escape_string(entity[key]) if entity[key] else ''
        unit_value_sql += '"%s",' % escape_value
      value_sql += '(%s),' %  unit_value_sql[:-1]

    return ' (%s) values %s ' % (key_sql[:-1],value_sql[:-1])

  @classmethod
  def get_condition_sql(cls,conditions):
    '''
    @description : get sql conditons
    @param {dict[]} conditions : one or more conditions
      [
        {'operator':'and','field':'name','comparator':'=','value':'blues'},
        {'operator':'and','field':'name','comparator':'=','value':'blues'}
      ] 
    @returns {str} : conditon sql
    '''
    sql = ''
    if not conditions:
      return sql 

    avail_condition_count = 0
    condition_list = [conditions] if isinstance(conditions,dict) else conditions 
    for condition in condition_list:
      field = condition.get('field')
      comparator = condition.get('comparator','=')
      operator = condition.get('operator','and')
      value_type = condition.get('value_type')

      if comparator == 'in':
        original_value = condition.get('value')
        if not original_value:
          continue

        value = cls.get_in_sql(field,original_value)
      else:
        value = condition.get('value','')

      if not field:
        continue

      if avail_condition_count==0:
        operator = ''

      avail_condition_count+=1
      if comparator=='in':
        sql += ' %s ( %s ) ' % (operator,value)
      else:
        if value_type=='function':
          sql += ' %s (%s %s %s) ' % (operator,field,comparator,value)
        else:
          sql += ' %s (%s %s "%s") ' % (operator,field,comparator,value)

    return ' where %s ' % sql

  @classmethod
  def get_limit_sql(cls,pagination):
    '''
    @description : get limit sql
    @param {dict} pagination : page info
      {'no':1,'size':10}
    @returns {str} : limit sql
    '''
    if not pagination:
      return ''

    no = int(pagination.get('no',1))
    size = int(pagination.get('size',50))
    from_index = (no-1)*size
    return ' limit %s,%s ' % (from_index,size)
    

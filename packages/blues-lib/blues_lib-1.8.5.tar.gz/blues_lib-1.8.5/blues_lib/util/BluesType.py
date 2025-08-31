class BluesType():

  @classmethod
  def last_index(cls,sequence,value):
    '''
    @description : get the last index of a value in a sequence
    @param {tuple|list} sequence
    @param {any} value
    @returns {init} : Returns -1 if there is no match
    '''
    try:
      return (len(sequence) - 1) - sequence[::-1].index(value)
    except ValueError:
      return -1 
 
  @classmethod
  def is_field_satisfied_dict(cls,value,keys,is_value_required=False):
    '''
    Is a valid dict that contains all required keys
    Parameter:
      value(dict) 
      keys(list) : the required keys
      is_value_required (bool) : the every required fields' value is required (don't support empty value)
    Returns
      bool
    '''
    if not value or not keys:
      return False

    for key in keys:
      if key not in value:
        return False
      if is_value_required:
        if not value.get(key):
          return False
    return True



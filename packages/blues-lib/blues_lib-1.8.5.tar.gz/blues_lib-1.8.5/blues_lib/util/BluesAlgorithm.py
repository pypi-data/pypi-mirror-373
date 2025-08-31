import hashlib
class BluesAlgorithm():

  @classmethod
  def md5(cls,text):
    # 单向不可逆，作为数据存储密码，如果忘了只能重置
    md_5 = hashlib.md5()
    # update入参必须时 bytes类型
    md_5.update(text.encode())
    return md_5.hexdigest()
  
  @classmethod
  def sha1(cls,text):
    sha_1 = hashlib.sha1()
    sha_1.update(text.encode())
    return sha_1.hexdigest()
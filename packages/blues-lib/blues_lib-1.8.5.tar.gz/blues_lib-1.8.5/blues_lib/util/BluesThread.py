from threading import Thread
import time

class BluesThread():

  @classmethod
  def run(cls,funcs=None):
    threads = []
    for func in funcs:
      thread = Thread(target=func)
      threads.append(thread)
      thread.start()

    for thread in threads:
      thread.join()

  @classmethod
  def test(cls):
    def fn1():
      for i in range(3):
        print('fn1:%s' % (i+1))
        time.sleep(1)

    def fn2():
      for i in range(3):
        print('fn2:%s' % (i+1))
        time.sleep(1)

    funcs = [fn1,fn2]
    print('==>start: %s' % time.ctime()) 
    cls.run(funcs)
    print('==>end: %s' % time.ctime()) 
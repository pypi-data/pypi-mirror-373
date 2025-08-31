import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from namespace.NSEnum import NSEnum
from namespace.EnumNS import EnumNS

class CommandName(EnumNS):
  
  class Exception(NSEnum):
    UNSET = "command.exception.unset"
    ABORT = "command.exception.abort"
    IGNORE = "command.exception.ignore" # ignore the exception
    SKIP = "command.exception.skip" # ignore and skip to do some next command
    
  class Control(NSEnum):
    BLOCKER = "command.control.blocker"
    RETRYER = "command.control.retryer"
    PRINTER = "command.control.printer"
    
  class Type(NSEnum):
    GETTER = "command.type.getter" # just read the output
    SETTER = "command.type.setter" # set the output
    ACTION = "command.type.action" # just exec, don't update the output
    
  class Flow(NSEnum):
    ENGINE = "command.flow.engine"
    QUEUE = "command.flow.queue"
    WHILE = "command.flow.while"

  class IO(NSEnum):
    INPUT = "command.io.input"
    OUTPUT = "command.io.output"
    
  class Browser(NSEnum):
    CREATOR = "command.browser.creator"
    
  class Crawler(NSEnum):
    BASE = "command.crawler.base"
    LOOP = "command.crawler.loop"
    DEPTH = "command.crawler.depth"
    ENGINE = "command.crawler.engine"
  
  # login crawler
  class Loginer(NSEnum):
    ACTOR = "command.loginer.actor"
    CHECKER = "command.loginer.checker"
    
  # material crawler
  class Material(NSEnum):
    SINKER = "command.material.sinker"
    QUERIER = "command.material.querier"

  class Notifier(NSEnum):
    EMAIL = "command.notifier.email"
  
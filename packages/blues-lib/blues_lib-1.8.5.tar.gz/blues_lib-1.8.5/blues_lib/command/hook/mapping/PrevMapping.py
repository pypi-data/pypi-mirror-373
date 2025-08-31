import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from namespace.CrawlerName import CrawlerName
from command.hook.mapping.AbsMapping import AbsMapping

class PrevMapping(AbsMapping):

  POSITION = CrawlerName.Field.PREV
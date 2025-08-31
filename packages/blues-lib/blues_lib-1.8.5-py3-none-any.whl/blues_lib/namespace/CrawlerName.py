import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from namespace.NSEnum import NSEnum
from namespace.EnumNS import EnumNS

class CrawlerName(EnumNS):
  # it's a filed level namespace

  # crawler engine
  class Engine(NSEnum):
    URL = "URL"
    LOOP = "LOOP"
    MAT_LOOP = "MAT_LOOP"
    DEPTH = "DEPTH"

  # static fields 
  class Field(NSEnum):
    PREV = "prev" # {dict} the prev node's config
    MAPPING = "mapping" # {dict} the mapping config

    POST = "post" # {dict} the post node's config
    PROCESSOR = "processor" # {dict} the processor config

    SUMMARY = "summary" # {dict} the info about the crawler
    # field in SUMMARY
    TYPE = "type" # {str} the type of crawler
    COUNT = "count" # {int} the count of crawler
    QUIT = "quit" # {bool} is quit the browser after crawled
    URLS = "urls" # {list[str]} the urls to crawl
    PAGES = "pages" # {list[dict]} the input list contains url and bizdata
    ENTITIES = "entities" # {list[dict]} the input list contains url field

    CRAWLER = "crawler" # {dict} the bhv executor's config
    CRAWLERS = "crawlers" # {list[dict]} the bhv executor's config
    METAS = "metas" # {list[dict]} the crawler meta config

    # field in CRAWLER
    SETUP = "setup" # {dict} the setup config
    DATA = "data" # {dict} the attr to save the crawled data dict
    TEARDOWN = "teardown" # {dict} the teardown config

    # field in SETUP
    URL = "url" # {str} the url to crawl
    BEFORE_CRAWLED = "before_crawled" # {dict} the config to run before crawled
    AFTER_CRAWLED = "after_crawled" # {dict} the config to run after crawled
    BEFORE_EACH_CRAWLED = "before_each_crawled" # {dict} the config to run before each crawled
    AFTER_EACH_CRAWLED = "after_each_crawled" # {dict} the config to run after each crawled

    # field in DATA
    LOGGEDIN = "loggedin" # {bool} is logged
    CKFILE = "ckfile" # {str} is local file to save the cookie file
    
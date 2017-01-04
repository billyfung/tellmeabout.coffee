from .intelli import scrape_intelli
from .stumptown import scrape_stumptown
from .victrola import scrape_victrola
from .heart import scrape_heart
from .bluebottle import scrape_bluebottle
from .fortyninth import scrape_fortyninth
from .matchstick import scrape_matchstick
from urllib3.connection import UnverifiedHTTPSConnection
from urllib3.connectionpool import HTTPSConnectionPool

# Override the default Connection class for the HTTPSConnectionPool.
HTTPSConnectionPool.ConnectionCls = UnverifiedHTTPSConnection

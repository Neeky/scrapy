"""
scrapy.telnet 已经不被推荐使用，现用scrapy.extensions.telnet 代替它
"""
import warnings
from scrapy.exceptions import ScrapyDeprecationWarning
warnings.warn("Module `scrapy.telnet` is deprecated, "
              "use `scrapy.extensions.telnet` instead",
              ScrapyDeprecationWarning, stacklevel=2)

from scrapy.extensions.telnet import *

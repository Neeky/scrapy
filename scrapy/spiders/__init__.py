"""
Base class for Scrapy spiders

See documentation in docs/topics/spiders.rst
"""
import logging
import warnings

from scrapy import signals
from scrapy.http import Request
from scrapy.utils.trackref import object_ref
from scrapy.utils.url import url_is_from_spider
from scrapy.utils.deprecate import create_deprecated_class
from scrapy.exceptions import ScrapyDeprecationWarning
from scrapy.utils.deprecate import method_is_overridden


class Spider(object_ref):
    """Base class for scrapy spiders. All spiders must inherit from this
    class.
    Spider类的作用是定义一个用户爬虫的统一接口
        1、处理http的响应(抽取数据)
    """

    name = None
    custom_settings = None

    def __init__(self, name=None, **kwargs):
        """
        初始化Spider类，并保证name,start_urls被赋值
        """
        #如果传入的name值不为空，那么就设置self.name为name
        #如果传入的name值为空  ，那么就测试有没有在类级别设置name的值
        if name is not None:
            self.name = name
        elif not getattr(self, 'name', None):
            raise ValueError("%s must have a name" % type(self).__name__)
        #根据kwargs更新实例的属性与值
        self.__dict__.update(kwargs)
        #测试是否有start_urls属性，如果没有就，增加并把属性的值设置为[]
        if not hasattr(self, 'start_urls'):
            self.start_urls = []

    @property
    def logger(self):
        """
        通过logging模块取得log对象
        """
        logger = logging.getLogger(self.name)
        return logging.LoggerAdapter(logger, {'spider': self})

    def log(self, message, level=logging.DEBUG, **kw):
        """Log the given message at the given log level

        This helper wraps a log call to the logger within the spider, but you
        can use it directly (e.g. Spider.logger.info('msg')) or use any other
        Python logger too.
        """
        self.logger.log(level, message, **kw)

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        """
        类方法、这个方法的作用是通过crawler参数来完成一个Spider对象的初始化.
        crawler 参数设置为Spider对象crawler属性的值
        """
        spider = cls(*args, **kwargs)
        spider._set_crawler(crawler)
        return spider

    def set_crawler(self, crawler):
        warnings.warn("set_crawler is deprecated, instantiate and bound the "
                      "spider to this crawler with from_crawler method "
                      "instead.",
                      category=ScrapyDeprecationWarning, stacklevel=2)
        assert not hasattr(self, 'crawler'), "Spider already bounded to a " \
                                             "crawler"
        self._set_crawler(crawler)

    def _set_crawler(self, crawler):
        self.crawler = crawler
        self.settings = crawler.settings
        crawler.signals.connect(self.close, signals.spider_closed)

    def start_requests(self):
        """
        生成器函数、返回由start_url确定的Request对象
        """
        cls = self.__class__
        if method_is_overridden(cls, Spider, 'make_requests_from_url'):
            warnings.warn(
                "Spider.make_requests_from_url method is deprecated; it "
                "won't be called in future Scrapy releases. Please "
                "override Spider.start_requests method instead (see %s.%s)." % (
                    cls.__module__, cls.__name__
                ),
            )
            for url in self.start_urls:
                yield self.make_requests_from_url(url)
        else:
            for url in self.start_urls:
                yield Request(url, dont_filter=True)

    def make_requests_from_url(self, url):
        """ This method is deprecated. """
        return Request(url, dont_filter=True)

    def parse(self, response):
        """
        抽取数据时的逻辑、交由子类实现。
        """
        raise NotImplementedError

    @classmethod
    def update_settings(cls, settings):
        settings.setdict(cls.custom_settings or {}, priority='spider')

    @classmethod
    def handles_request(cls, request):
        return url_is_from_spider(request.url, cls)

    @staticmethod
    def close(spider, reason):
        closed = getattr(spider, 'closed', None)
        if callable(closed):
            return closed(reason)

    def __str__(self):
        return "<%s %r at 0x%0x>" % (type(self).__name__, self.name, id(self))

    __repr__ = __str__


BaseSpider = create_deprecated_class('BaseSpider', Spider)


class ObsoleteClass(object):
    """
    只包了一个message属性，好像没有什么用!
    """
    def __init__(self, message):
        self.message = message

    def __getattr__(self, name):
        raise AttributeError(self.message)

spiders = ObsoleteClass(
    '"from scrapy.spider import spiders" no longer works - use '
    '"from scrapy.spiderloader import SpiderLoader" and instantiate '
    'it with your project settings"'
)

# Top-level imports
from scrapy.spiders.crawl import CrawlSpider, Rule
from scrapy.spiders.feed import XMLFeedSpider, CSVFeedSpider
from scrapy.spiders.sitemap import SitemapSpider

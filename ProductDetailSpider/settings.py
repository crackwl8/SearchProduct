# -*- coding: utf-8 -*-

# Scrapy settings for searchActivity project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#     http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
#     http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'ProductDetailSpider'

SPIDER_MODULES = ['ProductDetailSpider.spiders']
NEWSPIDER_MODULE = 'ProductDetailSpider.spiders'

DOWNLOAD_DELAY = 1  # 间隔时间
LOG_LEVEL = 'DEBUG'  # 日志级别
CONCURRENT_REQUESTS = 100  # 默认为16
# CONCURRENT_ITEMS = 1
# CONCURRENT_REQUESTS_PER_IP = 1
REDIRECT_ENABLED = True
# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'SearchActivity (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

RETRY_ENABLED = False

DOWNLOADER_MIDDLEWARES = {
    'ProductDetailSpider.middlewares.ProxyMiddleware': 100,
    "ProductDetailSpider.middlewares.UserAgentMiddleware": 401,
    "ProductDetailSpider.middlewares.CookiesMiddleware": 402,
    'ProductDetailSpider.middlewares.JavaScriptMiddleware': 403,
}
ITEM_PIPELINES = {
    "ProductDetailSpider.pipelines.SearchActivityMongoDBPipeline": 413,
}

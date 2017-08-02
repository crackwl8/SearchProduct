#coding:utf-8
import requests
import logging
from scrapy.http import HtmlResponse
from scrapy.spiders import CrawlSpider
from scrapy.selector import Selector
from ProductDetailSpider.items import ProductItem, ProductStockItem
from ProductDetailSpider.search_type import PH_TYPES, TMALL_DESC, TMALL_EXCEPT_DOMAIN, JD_DESC, JD_EXCEPT_DOMAIN, AMAZON_DESC, AMAZON_EXCEPT_DOMAIN
from scrapy.http import Request
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError, TCPTimedOutError
import re
import json
import random
import time
from selenium import webdriver

web_driver = webdriver.Chrome("/Users/wulei/Downloads/chromedriver")

class Spider(CrawlSpider):
    name = 'ProductDetailSpider'
    allowed_domains = ['tmall.com', 'taobao.com', 'jd.com', 'amazon.cn']
    start_urls = []
    logging.getLogger("requests").setLevel(logging.WARNING
                                          )  # 将requests的日志级别设成WARNING
    logging.basicConfig(
        level=logging.INFO,
        format=
        '%(asctime)s %(filename)s[line:%(lineno)d] %(process)d %(thread)d %(levelname)s %(message)s',
        datefmt='%a, %d %b %Y %H:%M:%S',
        filename='cataline.log',
        filemode='w')

    def __init__(self):  # 初始化类
        self.waiting_list = []
        self.finish_list = []
        self.driver = web_driver
        self.driver.set_page_load_timeout(20)
        self.driver.set_script_timeout(5)

    def __del__(self):
        if self.driver is not None:
            self.driver.quit()

    # test = True
    def start_requests(self):
        hosts = [
                 {'url': 'https://www.amazon.com/gp/product/B00YPVYUSI/ref=ox_sc_act_image_2?smid=A2IRACCYJ5AYVC&psc=1', 'call_back': self.parse_amazon_foreign_key},
                ]
        for host in hosts:
            self.waiting_list.append(host['url'])
            yield Request(url='%s' % (host['url']),
                          callback=host['call_back'], errback=self.parse_err)

    def parse_err(self, failure):
        # log all failures
        # logging.error(repr(failure))
        url = ''
        # in case you want to do something special for some errors,
        # you may need the failure's type:

        if failure.check(HttpError):
            # these exceptions come from HttpError spider middleware
            # you can get the non-200 response
            response = failure.value.response
            url = response.url
            # selector = Selector(response)
            # logging.info(selector)
            logging.error('HttpError on %s', response.url)

        elif failure.check(DNSLookupError):
            # this is the original request
            request = failure.request
            url = request.url
            logging.error('DNSLookupError on %s', request.url)

        elif failure.check(TimeoutError, TCPTimedOutError):
            request = failure.request
            url = request.url
            logging.error('TimeoutError on %s', request.url)

        if url:
            try:
                self.waiting_list.remove(url)
            except ValueError:
                # logging.debug(self.waiting_list)
                pass
            self.finish_list.append(url)
        logging.debug('request url err callback:------>' + url + ' waiting %s finished %s' % (len(self.waiting_list), len(self.finish_list)))


    def parse_amazon_info(self, response):
        actItem = ProductItem()
        selector = Selector(response)
        _ph_info = selector.xpath('//title/text()').extract()
        title = _ph_info[0]
        actItem['title'] = title
        image_url = ''
        actItem['image_url'] = image_url
        link_url = response.url
        actItem['link_url'] = link_url
        actItem['website'] = 'amazon'
        actItem['valid'] = True
        import string
        prices = selector.css('span#priceblock_ourprice.a-size-medium.a-color-price::text').extract()
        if prices and len(prices) > 0:
            price = prices[0][1:]
        actItem['price'] = string.atof(price)
        logging.debug(' title:%s link_url:%s price:%s' % (title, link_url, price))
        return actItem

    def get_quantity(self, response):
        selector = Selector(response)
        addCartForm = selector.css('form#addToCart.a-content').extract()

        # logging.debug(' addCartForm:%s' % (addCartForm))
        try:
            btn = self.driver.find_element_by_id('add-to-cart-button').click()
            response = self.driver.page_source
            url = self.driver.current_url
            if url == 'https://www.amazon.com/gp/cart/view.html/ref=lh_cart_vc_btn':
                from selenium.webdriver.support.ui import Select
                s1 = Select(self.driver.find_element_by_name('quantity'))  # 实例化Select
                s1.select_by_value("10")  # 选择value="o2"的项
            elif 'https://www.amazon.com/gp/huc/view.html' in url:
                url == 'https://www.amazon.com/gp/cart/view.html/ref=lh_cart_vc_btn'
                self.driver.find_element_by_id('hlb-view-cart-announce').click()
                from selenium.webdriver.support.ui import Select
                s1 = Select(self.driver.find_element_by_name('quantity'))  # 实例化Select
                s1.select_by_value("10")  # 选择value="o2"的项
                self.driver.find_element_by_name('quantityBox').send_keys("999")
                self.driver.find_element_by_id('a-autoid-3-announce').click()

                time.sleep(1)
                url_list = re.findall(ur'input type=\"text\" maxlength=\"3\" value=\"(.*?)\"', self.driver.page_source.encode('UTF-8', 'ignore'), re.S)
                stock = url_list[0]

                self.driver.find_element_by_xpath('//span[@class=\"a-declarative\"]/input').click()
            else:
                logging.error(' addCartForm error, wrong url %s' % (url))
        except Exception as exc:
            logging.error(' get_quantity error, wrong %s' % exc)

    def parse_amazon_foreign_key(self, response):
        selector = Selector(response)
        try:
            self.waiting_list.remove(response.url)
        except ValueError:
            # logging.debug(self.waiting_list)
            pass
        self.finish_list.append(response.url)
        logging.info(
            ' request url callback:----->' + response.url + ' waiting %s finished %s' % (len(self.waiting_list), len(self.finish_list)))

        # logging.info(selector)
        # divs = selector.xpath('//div[@class="tm-fcs-panel"]/dl[@class="tm-promo-panel"]/dd/div[@class="tm-promo-price"]')
        viewkey = None
        price = 0
        # 商品详情的页面才处理，要取出价格、卖家、品牌、评论、库存等信息
        if 'www.amazon.com/dp/product' in response.url or 'www.amazon.com/gp/product' in response.url:

            self.get_quantity(response)
            yield self.parse_amazon_info(response)





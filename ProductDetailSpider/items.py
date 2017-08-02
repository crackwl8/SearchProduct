# -*- coding: utf-8 -*-

from scrapy import Item, Field


class ProductItem(Item):
    title = Field()
    image_url = Field()
    link_url = Field()
    website = Field()
    valid = Field()
    price = Field()
    product_id = Field()


class ProductStockItem(Item):
    title = Field()
    product_id = Field()
    stock = Field()
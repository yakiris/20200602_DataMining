# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class BookparserItem(scrapy.Item):
    # define the fields for your item here like:
    _id = scrapy.Field()
    name = scrapy.Field()
    author = scrapy.Field()
    year = scrapy.Field()
    publisher = scrapy.Field()
    feature = scrapy.Field()
    key = scrapy.Field()
    rating = scrapy.Field()
    pages = scrapy.Field()
    price = scrapy.Field()
    link = scrapy.Field()


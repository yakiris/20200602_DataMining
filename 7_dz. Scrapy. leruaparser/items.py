# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import MapCompose, TakeFirst

def coversion_int(elem):
    return int(elem.replace(' ', ''))

def coversion_str(elem):
    elem = ' '.join(list(filter(None, elem.replace('\n', '').split(' '))))
    return elem

class LeruaparserItem(scrapy.Item):
    # define the fields for your item here like:
    _id = scrapy.Field()
    name = scrapy.Field(output_processor=TakeFirst())
    link = scrapy.Field(output_processor=TakeFirst())
    price = scrapy.Field(input_processor=MapCompose(coversion_int), output_processor=TakeFirst())
    photos = scrapy.Field()
    param_key = scrapy.Field()
    param_value = scrapy.Field(input_processor=MapCompose(coversion_str))
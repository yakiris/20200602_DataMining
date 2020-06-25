# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import scrapy
from scrapy.pipelines.images import ImagesPipeline
from pymongo import MongoClient

class LeruaparserPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongo_base = client.lerua_scrapy

    def process_item(self, item, spider):
        item_pars = {}
        item_pars['name'] = item['name']
        item_pars['link'] = item['link']
        item_pars['price'] = item['price']
        index = 0
        for i in item['param_key']:
            item_pars[i] = item['param_value'][index]
            index += 1

        collection = self.mongo_base[spider.name]
        collection.replace_one(item_pars, item_pars, upsert=True)

        return item_pars

class LeruaparserPhotosPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        if item['photos']:
            for img in item['photos']:
                try:
                    yield scrapy.Request(img, meta=item)
                except Exception as e:
                    print(e)

    def file_path(self, request, response=None, info=None):
        folder = request.meta['name']
        index = str(request)[-7:-5]
        return f'{folder}/{index}.jpg'

    def item_completed(self, results, item, info):
        if results:
            item['photos'] = [itm[1] for itm in results if itm[0]]
        return item
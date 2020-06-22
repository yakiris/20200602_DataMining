# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from pymongo import MongoClient

class BookparserPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongo_base = client.book_scrapy

    def process_item(self, item, spider):
        item_scrapy = {}
        item_scrapy['link'] = item['link']
        if spider.name == 'book24':
            item_scrapy['source'] = 'book24'
            item_scrapy['name'] = item['name']
            item_scrapy['author'] = item['key'][0]
            index = 0
            for feature in item['feature']:
                if 'Год издания:' in feature:
                    item_scrapy['year'] = item['feature'][index + 1]
                if 'Количество страниц:' in feature:
                    item_scrapy['pages'] = item['feature'][index + 1]
                index += 1
            item_scrapy['publisher'] = item['key'][3].replace('\n', '').strip()
            item_scrapy['rating'] = item['rating']
            item_scrapy['price'] = item['price'].replace(' ', '')
        elif spider.name == 'labirint':
            item_scrapy['source'] = 'labirint'
            item_scrapy['name'] = item['name'].split(':')[1]
            item_scrapy['author'] = item['author']
            item_scrapy['price'] = item['price']
            item_scrapy['publisher'] = item['publisher']
            item_scrapy['year'] = item['year'][1][2:-3]
            item_scrapy['pages'] = item['pages'][0].split(' ')[1]
            item_scrapy['rating'] = item['rating']

        collection = self.mongo_base[spider.name]
        collection.replace_one(item_scrapy, item_scrapy, upsert=True)

        return item_scrapy

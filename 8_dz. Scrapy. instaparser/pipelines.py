# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import scrapy
from scrapy.pipelines.images import ImagesPipeline
from pymongo import MongoClient

class InstaparserPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongo_base = client.insta_scrapy

    def process_item(self, item, spider):
        item_pars = {}
        item_pars['user_id'] = item['user_id']
        item_pars['following_id'] = item['following_id']
        item_pars['following_name'] = item['following_name']
        item_pars['follower_id'] = item['follower_id']
        item_pars['follower_name'] = item['follower_name']

        collection = self.mongo_base['follow']
        collection.replace_one(item_pars, item_pars, upsert=True)

        collection_node = self.mongo_base['node']
        collection_node.replace_one(item['node'], item['node'], upsert=True)

        return item_pars

class InstaparserPhotosPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        if item['node']['profile_pic_url']:
            try:
                yield scrapy.Request(item['node']['profile_pic_url'], meta=item)
            except Exception as e:
                print(e)

    def file_path(self, request, response=None, info=None):
        image_name = request.meta['node']['id']
        return f'/{image_name}.jpg'

    def item_completed(self, results, item, info):
        if results:
            item['node']['profile_pic_url'] = [itm[1] for itm in results if itm[0]]
        return item
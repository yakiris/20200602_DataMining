# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from datetime import datetime, timedelta
from pymongo import MongoClient

def convers(month):
    if month == '01':
        month_c = 'января'
    elif month == '02':
        month_c = 'февраля'
    elif month == '03':
        month_c = 'марта'
    elif month == '04':
        month_c = 'апреля'
    elif month == '05':
        month_c = 'мая'
    elif month == '06':
        month_c = 'июня'
    elif month == '07':
        month_c = 'июля'
    elif month == '08':
        month_c = 'августа'
    elif month == '09':
        month_c = 'сентября'
    elif month == '10':
        month_c = 'октября'
    elif month == '11':
        month_c = 'ноября'
    elif month == '12':
        month_c = 'декабря'
    return month_c

class JobparserPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongo_base = client.vacansy_scrapy

    def process_item(self, item, spider):
        item_scrapy = {}
        item_scrapy['date_update'] = datetime.now().strftime('%d.%m.%Y')
        item_scrapy['name'] = item['name']
        item_scrapy['link'] = item['link']
        item_scrapy['city'] = " ".join(item['city'])
        company = item['company']
        salary = item['salary']
        date = item['date']

        if spider.name == 'hhru':
            item_scrapy['source'] = 'hh.ru'
            if len(date) == 1:
                item_scrapy['date'] = date[0].split(' ')[2] + ' ' + date[0].split(' ')[3]
            else:
                item_scrapy['date'] = date[1].replace('\xa0', ' ')[:-5]
            if len(company) == 1:
                item_scrapy['company'] = company[0]
            else:
                item_scrapy['company'] = company[len(company) - 1]
            if 'з/п не указана' in item['salary'][0]:
                item_scrapy['salary_min'] = None
                item_scrapy['salary_max'] = None
                item_scrapy['currency'] = None
            elif len(salary) == 7:
                item_scrapy['salary_min'] = salary[1].replace('\xa0', '')
                item_scrapy['salary_max'] = salary[3].replace('\xa0', '')
                item_scrapy['currency'] = item['salary'][5]
            elif len(salary) == 5:
                if 'от' in salary[0]:
                    item_scrapy['salary_min'] = salary[1].replace('\xa0', '')
                    item_scrapy['salary_max'] = None
                elif 'до' in salary[0]:
                    item_scrapy['salary_min'] = None
                    item_scrapy['salary_max'] = salary[1].replace('\xa0', '')
                item_scrapy['currency'] = item['salary'][3]
        else:
            item_scrapy['source'] = 'sj.ru'
            date = date[2]
            if 'сегодня' in date:
                item_scrapy['date'] = datetime.now().strftime('%d') + ' ' + convers(datetime.now().strftime('%m'))
            elif 'вчера' in date:
                yesterday = datetime.now() - timedelta(days=1)
                item_scrapy['date'] = yesterday.strftime('%d') + ' ' + convers(yesterday.strftime('%m'))
            else:
                item_scrapy['date'] = date
            item_scrapy['company'] = company[0]
            if 'По договорённости' in salary:
                item_scrapy['salary_min'] = None
                item_scrapy['salary_max'] = None
                item_scrapy['currency'] = None
            elif len(salary) == 4:
                item_scrapy['salary_min'] = salary[0].replace('\xa0', '')
                item_scrapy['salary_max'] = salary[1].replace('\xa0', '')
                item_scrapy['currency'] = salary[3]
            elif len(salary) == 3:
                item_scrapy['currency'] = salary[2].split('\xa0')[-1:][0]
                if 'от' in salary[0]:
                    item_scrapy['salary_min'] = salary[2].split('\xa0')[0] + '' + salary[2].split('\xa0')[1]
                    item_scrapy['salary_max'] = None
                elif 'до' in salary[0]:
                    item_scrapy['salary_min'] = None
                    item_scrapy['salary_max'] = salary[2].split('\xa0')[0] + '' + salary[2].split('\xa0')[1]

        collection = self.mongo_base[spider.name]
        collection.replace_one(item_scrapy, item_scrapy, upsert=True)

        collection.delete_many({'date_update': {'$lt': datetime.now().strftime('%d.%m.%Y')}})

        return item_scrapy
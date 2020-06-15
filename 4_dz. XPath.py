from pprint import pprint
from lxml import html
import requests
from datetime import datetime
from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client['news']
news = db.news

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

header = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36'}

links = []

lenta = 'https://lenta.ru'
response_l = requests.get(lenta + '/',  headers=header)
dom_l = html.fromstring(response_l.text)
blocks_l = dom_l.xpath("//div[@class='item news b-tabloid__topic_news']")

for block in blocks_l:
    item_l = {}
    item_l['source'] = lenta[8:]
    name = block.xpath(".//div[@class='titles']//a/span/text()")
    item_l['name'] = name[0].replace("\xa0", ' ')
    a = block.xpath(".//div[@class='titles']//a/@href")
    if 'https' in a[0]:
        item_l['link'] = a[0]
    else:
        item_l['link'] = lenta + a[0]
    date = block.xpath(".//span[@class='g-date item__date']/text()")
    if date[0] == 'Сегодня':
        date_r =  datetime.now().strftime('%d') + ' ' + convers(datetime.now().strftime('%m'))
    else:
        date_r = date[0]
    time = block.xpath(".//span[@class='g-date item__date']//text()")
    item_l['date'] = date_r
    item_l['time'] = time[0]
    links.append(item_l)

yandex = 'https://yandex.ru'
response_y = requests.get(yandex + '/news/',  headers=header)
dom_y = html.fromstring(response_y.text)
blocks_y = dom_y.xpath("//div[@class='story__topic']")

for block in blocks_y:
    item_y = {}

    name = block.xpath(".//h2[@class ='story__title']//a[1]/text()")
    item_y['name'] = name[0]

    a = block.xpath(".//h2[@class ='story__title']//a[1]/@href")
    link = a[0][:a[0].index('?')]
    item_y['link'] = yandex + link

    info = block.xpath("./../div[@class = 'story__info']//div[1]/text()")

    date = info[0].rsplit(' ', 1)[1]
    if len(date) == 5:
        item_y['date'] = datetime.now().strftime('%d') + ' ' + convers(datetime.now().strftime('%m'))
        item_y['time'] = date
    else:
        item_y['date'] = date.replace("\xa0", ' ')[:-8]
        item_y['time'] = date[-5:]

    source = info[0].rsplit(' ', 1)[0]
    item_y['source'] = source

    links.append(item_y)

mail = 'https://news.mail.ru'
response_m = requests.get(mail + '/',  headers=header)
dom_m = html.fromstring(response_m.text)
blocks_m = dom_m.xpath("//li[@class='list__item'] | //li[@class='list__item hidden_small']")

for block in blocks_m:
    item_m = {}

    name = block.xpath("./a[@class ='list__text']/text() | .//span[@class ='link__text']/text()")[0]
    item_m['name'] = name.replace("\xa0", ' ')

    link = block.xpath(".//a[@class ='list__text']/@href | .//a[@class ='link link_flex']/@href")[0]
    item_m['link'] = mail + link

    response_m2 = requests.get(mail + link, headers=header)
    dom_m2 = html.fromstring(response_m2.text)
    blocks_m2 = dom_m2.xpath("//div[@class='breadcrumbs breadcrumbs_article js-ago-wrapper']")

    for block2 in blocks_m2:

        source = block2.xpath(".//span[@class='link__text']/text()")
        item_m['source'] = source[0]

        date = block2.xpath(".//span[@class='note__text breadcrumbs__text js-ago']/@datetime")
        item_m['date'] = date[0][8:10] + ' ' + convers(date[0][5:7])
        item_m['time'] = date[0][11:16]

    links.append(item_m)

for link in links:
    news.insert_one(link)

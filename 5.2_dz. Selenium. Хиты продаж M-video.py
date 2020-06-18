#2) Написать программу, которая собирает «Хиты продаж» с сайта техники mvideo и складывает данные в БД.
# Магазины можно выбрать свои. Главный критерий выбора: динамически загружаемые товары

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from pymongo import MongoClient
from pprint import pprint

client = MongoClient('localhost', 27017)
db = client['bestseller']
bestseller = db.bestseller

chrome_options = Options()
chrome_options.add_argument('start-maximized')
driver = webdriver.Chrome(options = chrome_options)

driver.get('https://www.mvideo.ru/')

hit_block = driver.find_elements_by_class_name('section')

while True:
    try:
        button = hit_block[4].find_elements_by_class_name('sel-hits-button-next')[0]
        button.click()
    except:
        break

time.sleep(3)
blocks = hit_block[4].find_elements_by_class_name('sel-product-tile-main')

for block in blocks:
    item = {}
    name = block.find_element_by_tag_name('h4')
    item['name'] = name.text
    price = block.find_element_by_class_name('c-pdp-price__current')
    item['price'] = price.text
    bestseller.insert_one(item)
    time.sleep(2)

driver.quit()

for hit in bestseller.find({}):
    pprint(hit)

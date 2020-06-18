#1) Написать программу, которая собирает входящие письма из своего или тестового почтового ящика
# и сложить данные о письмах в базу данных
# * от кого,
# * дата отправки,
# * тема письма,
# * текст письма полный

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
import time
from datetime import datetime
from pymongo import MongoClient
from pprint import pprint

client = MongoClient('localhost', 27017)
db = client['letters']
letters = db.letters

chrome_options = Options()
chrome_options.add_argument('start-maximized')

driver = webdriver.Chrome(options = chrome_options)

driver.get('https://mail.ru')

assert "Mail" in driver.title

login = driver.find_element_by_id('mailbox:login')
login.send_keys('study.ai_172@mail.ru')

elem = driver.find_element_by_id('mailbox:submit')
elem.click()
time.sleep(5)

password = driver.find_element_by_id('mailbox:password')
password.send_keys('NextPassword172')

elem.click()
time.sleep(5)

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

links = []
for i in range(3):
    time.sleep(5)
    articles = driver.find_elements_by_class_name('js-tooltip-direction_letter-bottom')
    for articl in articles:
        links.append(articl.get_attribute('href'))
    actions = ActionChains(driver)
    actions.move_to_element(articles[-1])
    actions.perform()

for link in links:
    item = {}
    driver.get(link)
    time.sleep(5)
    item['author'] = driver.find_element_by_class_name('letter-contact').text
    date = driver.find_element_by_class_name('letter__date').text
    if 'Сегодня' in date:
        date1 = datetime.now().strftime('%d') + ' ' + convers(datetime.now().strftime('%m')) + ', '+ date[-5:]
    else:
        date1 = date
    item['date'] = date1
    item['subject'] = driver.find_element_by_tag_name('h2').text
    item['text'] = driver.find_element_by_class_name('letter__body').text

    letters.insert_one(item)

driver.quit()

for letter in letters.find({}):
    pprint(letter)
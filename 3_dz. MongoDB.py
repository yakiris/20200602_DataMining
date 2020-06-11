# 1) Развернуть у себя на компьютере/виртуальной машине/хостинге MongoDB и реализовать функцию, записывающую собранные вакансии в созданную БД
# 2) Написать функцию, которая производит поиск и выводит на экран вакансии с заработной платой больше введенной суммы
# 3*)Написать функцию, которая будет добавлять в вашу базу данных только новые вакансии с сайта

from bs4 import BeautifulSoup as bs
import requests
import pandas as pd
from pymongo import MongoClient
from pprint import pprint

client = MongoClient('localhost', 27017)
db = client['vacancies']

vacancies = db.vacancies

us_vacancy = input('Введите вакансию для поиска: ')
next_page_hh = 0
main_link_hh = 'https://hh.ru'
header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36',
          'Accept': '*/*'}

def parse_salary(salary):
    salary = salary.replace("\xa0", '')
    salary_list = salary.split()
    salary_cur = salary_list.pop(len(salary_list) - 1)
    if '-' in salary:
        text = ''.join(salary_list).split('-')
        salary_min = int(text[0])
        salary_max = int(text[1])
    elif 'от' in salary:
        salary_min = int(salary_list[1])
        salary_max = None
    elif 'до' in salary:
        salary_min = None
        salary_max = int(salary_list[1])
    else:
        salary_min = None
        salary_max = None

    return salary_min, salary_max, salary_cur

vacancy_list = []

while True:
    params = {'text': us_vacancy,
              'page': next_page_hh}
    response = requests.get(main_link_hh + '/search/vacancy', params=params, headers=header)
    soup = bs(response.text, 'lxml')
    vacancy_block = soup.find('div', {'class': 'vacancy-serp'})

    for vacancy in vacancy_block.findAll('div', {'data-qa': 'vacancy-serp__vacancy'}): #Children(recursive=False):

        vacancy_data = {}

        vacancy_data['site'] = 'hh.ru'

        name = vacancy.find('a', {'data-qa': 'vacancy-serp__vacancy-title'})
        if name:
            vacancy_data['name'] = name.getText()
        else:
            continue

        salary = vacancy.find('span', {'data-qa': 'vacancy-serp__vacancy-compensation'})
        if salary:
            vacancy_data['salary_min'], vacancy_data['salary_max'], vacancy_data['salary_cur'] = \
                parse_salary(salary.getText())
        else:
            vacancy_data['salary_min'] = None
            vacancy_data['salary_max'] = None
            vacancy_data['salary_cur'] = None

        date = vacancy.find('span', {'data-qa': 'vacancy-serp__vacancy-date'})
        if date:
            vacancy_data['date'] = date.getText().replace('\xa0', ' ')
        else:
            vacancy_data['date'] = None

        employer = vacancy.find('a', {'data-qa': 'vacancy-serp__vacancy-employer'})
        if employer:
            vacancy_data['employer'] = employer.getText()
        else:
            vacancy_data['employer'] = None

        address = vacancy.find('span', {'data-qa': 'vacancy-serp__vacancy-address'})
        if address:
            vacancy_data['address'] = address.getText()
        else:
            vacancy_data['address'] = None

        link_fool = vacancy.find('a', {'data-qa': 'vacancy-serp__vacancy-title'})['href']
        if link_fool:
            link = link_fool[:link_fool.index('?')]
            vacancy_data['link'] = link
        else:
            vacancy_data['link'] = None

        vacancy_list.append(vacancy_data)

    has_next_page = soup.find('a', {'data-qa': 'pager-next'})
    if has_next_page:
        next_page_hh += 1
    else:
        break

for vacanc in vacancy_list:
    vacancies.replace_one(vacanc, vacanc, upsert=True)

sal = int(input('Зарплата от: '))

for vacancy in vacancies.find({'$or':[ {'salary_max': None, 'salary_min': {'$gt': sal}}, {'salary_min': None, 'salary_max': {'$gt': sal}}, \
                                       {'salary_max': {'$gt': sal}} ]}):
    pprint(vacancy)
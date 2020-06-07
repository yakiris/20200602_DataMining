# 1) Необходимо собрать информацию о вакансиях на вводимую должность (используем input или через аргументы) с сайта
# superjob.ru и hh.ru. Приложение должно анализировать несколько страниц сайта(также вводим через input или аргументы).
# Получившийся список должен содержать в себе минимум:
#     *Наименование вакансии
#     *Предлагаемую зарплату (отдельно мин. и отдельно макс.)
#     *Ссылку на саму вакансию
#     *Сайт откуда собрана вакансия
# По своему желанию можно добавить еще работодателя и расположение. Данная структура должна быть одинаковая для вакансий
# с обоих сайтов. Общий результат можно вывести с помощью dataFrame через pandas.
#
# !!!В первую очередь делаем сайт hh.ru - его обязательно. sj.ru можно попробовать сделать вторым. Он находится в очень
# странном состоянии и возможна некорректная работа.!!!

from bs4 import BeautifulSoup as bs
import requests
import pandas as pd

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
        salary_min = text[0]
        salary_max = text[1]
    elif 'от' in salary:
        salary_min = salary_list[1]
        salary_max = None
    elif 'до' in salary:
        salary_min = None
        salary_max = salary_list[1]
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

    for vacancy in vacancy_block.findChildren(recursive=False):

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

df_vacancy_list = pd.DataFrame(vacancy_list)

print(df_vacancy_list)

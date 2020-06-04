# 2. Изучить список открытых API. Найти среди них любое, требующее авторизацию (любого типа). Выполнить запросы к нему,
# пройдя авторизацию. Ответ сервера записать в файл.

import requests

id = '2541'
params = {'api_key': '626ed9eb77d4b24e87489337b0299c68',
          '$top': '10',
          '$orderby': 'global_id'}

main_link = 'https://apidata.mos.ru/v1/datasets/'+id+'/rows'
response = requests.get(main_link, params=params)

with open('1.2_dz. data.mos.ru.json', 'wb') as f:
    f.write(response.content)
data = response.json()

print('Археологические находки на реконструируемых улицах Москвы.')
for i in data:
    print(f'{i["Cells"]["DateOfDiscovery"]} - {i["Cells"]["DescriptionOfFinding"]}')